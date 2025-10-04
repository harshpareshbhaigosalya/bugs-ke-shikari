# backend/app.py
import os, json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity
)
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)
# Example DATABASE_URL: mysql+pymysql://root:password@localhost/expense_tracker_db
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') or "sqlite:///local_expense.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY') or "super-secret-jwt"
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or "super-secret"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# --------------------
# Models
# --------------------
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(100))
    currency = db.Column(db.String(3), default='USD')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='employee')  # superadmin, admin, manager, employee
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_manager_approver = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def check_password(self, pwd):
        return bcrypt.check_password_hash(self.password_hash, pwd)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Numeric(12,2), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    amount_in_company_currency = db.Column(db.Numeric(12,2), nullable=True)
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    expense_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')  # pending/approved/rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Approval(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expense.id'))
    approver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sequence_order = db.Column(db.Integer)
    status = db.Column(db.String(20), default='waiting')  # waiting/pending/approved/rejected/skipped
    comment = db.Column(db.Text)
    decided_at = db.Column(db.DateTime, nullable=True)

class CompanyApprover(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    approver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    step_order = db.Column(db.Integer)

class ApprovalRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    rule_type = db.Column(db.String(20), default='percentage')  # percentage | specific | hybrid
    percentage_threshold = db.Column(db.Integer, default=100)
    specific_approver_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- Receipt and AuditLog models ---
class Receipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expense.id'))
    file_path = db.Column(db.String(255), nullable=False)
    ocr_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --------------------
# Helpers
# --------------------
def get_current_user():
    uid = get_jwt_identity()
    if not uid: 
        return None
    return User.query.get(uid)

def create_approval_entries_for_expense(expense):
    """
    Create Approval rows for an expense:
     - If employee has manager and manager.is_manager_approver -> manager is first approver
     - Then company_approvers in configured order are appended
     The first created actionable approver will be set to 'pending', others 'waiting'
    """
    user = User.query.get(expense.user_id)
    seq = 1
    created = []
    # manager first if flagged
    if user and user.manager_id:
        m = User.query.get(user.manager_id)
        if m and m.is_manager_approver:
            a = Approval(expense_id=expense.id, approver_id=m.id, sequence_order=seq, status='pending')
            db.session.add(a); created.append(a); seq += 1

    # then company approvers
    caps = CompanyApprover.query.filter_by(company_id=expense.company_id).order_by(CompanyApprover.step_order).all()
    for cap in caps:
        # skip duplicate if same as manager already added
        if any((c.approver_id == cap.approver_id) for c in created):
            continue
        # if no pending yet, make this pending
        status = 'pending' if not any((c.status == 'pending') for c in created) else 'waiting'
        a = Approval(expense_id=expense.id, approver_id=cap.approver_id, sequence_order=seq, status=status)
        db.session.add(a); created.append(a); seq += 1
    db.session.commit()
    return created

def evaluate_expense_post_approval(expense):
    """
    After any approval decision, check approval_rules for company and finalize
    Implemented rules:
      - percentage: if approved_count / total_required >= threshold -> approved
      - specific: if specific approver approved -> approved
      - hybrid: either of above
    If final decision -> update expense.status and mark other pending approvals as 'skipped'
    """
    approvals = Approval.query.filter_by(expense_id=expense.id).all()
    rule = ApprovalRule.query.filter_by(company_id=expense.company_id).first()
    if not rule:
        # default -> all approvers must approve (100%)
        threshold = 100
        specific = None
        rtype = 'percentage'
    else:
        threshold = rule.percentage_threshold
        specific = rule.specific_approver_id
        rtype = rule.rule_type

    # compute totals ignoring skipped
    actionable = [a for a in approvals if a.status in ('pending','approved','rejected','waiting')]
    total = len(actionable)
    approved_count = len([a for a in approvals if a.status == 'approved'])
    # check specific approver
    specific_ok = False
    if specific:
        sp = next((a for a in approvals if a.approver_id == specific and a.status == 'approved'), None)
        specific_ok = sp is not None

    percent_ok = (total > 0) and ((approved_count / total) * 100 >= threshold)

    final_ok = False
    if rtype == 'percentage':
        final_ok = percent_ok
    elif rtype == 'specific':
        final_ok = specific_ok
    elif rtype == 'hybrid':
        final_ok = percent_ok or specific_ok

    if final_ok:
        expense.status = 'approved'
        db.session.add(expense)
        # mark all waiting/pending approvals as skipped (if not approved)
        for a in approvals:
            if a.status in ('waiting','pending') and a.status != 'approved':
                a.status = 'skipped'
                db.session.add(a)
        db.session.commit()
        return 'approved'
    else:
        # If any approval was rejected -> mark expense rejected immediately
        rejected = any(a.status == 'rejected' for a in approvals)
        if rejected:
            expense.status = 'rejected'
            db.session.add(expense)
            db.session.commit()
            return 'rejected'
    # otherwise still pending
    return 'pending'

def set_next_pending(expense):
    # make next waiting approval (lowest sequence_order with status 'waiting') -> 'pending'
    next_wait = Approval.query.filter_by(expense_id=expense.id, status='waiting').order_by(Approval.sequence_order).first()
    if next_wait:
        next_wait.status = 'pending'
        db.session.add(next_wait)
        db.session.commit()

# --------------------
# Auth & user endpoints
# --------------------
@app.route('/auth/register', methods=['POST'])
def register_company_admin():
    """
    Create a new company + admin user on first signup.
    Body: { company_name, country (optional), currency (optional ISO3), name, email, password }
    """
    data = request.json or {}
    company_name = data.get('company_name')
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    country = data.get('country')
    currency = data.get('currency') or 'USD'
    if not (company_name and name and email and password):
        return jsonify({"msg":"company_name,name,email,password required"}), 400

    # create company
    comp = Company(name=company_name, country=country, currency=currency)
    db.session.add(comp); db.session.commit()
    # create admin user (role = admin)
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(company_id=comp.id, name=name, email=email, password_hash=pw_hash, role='admin')
    db.session.add(user); db.session.commit()
    # default approval rule for company (all must approve)
    rule = ApprovalRule(company_id=comp.id, rule_type='percentage', percentage_threshold=100)
    db.session.add(rule); db.session.commit()

    access = create_access_token(identity=user.id, additional_claims={"role": user.role, "company_id": comp.id})
    return jsonify({"msg":"company+admin created", "access_token": access, "user": {"id": user.id, "email": user.email, "role":user.role}}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json or {}
    email = data.get('email'); password = data.get('password')
    if not (email and password):
        return jsonify({"msg":"email and password required"}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"msg":"invalid credentials"}), 401
    access = create_access_token(identity=user.id, additional_claims={"role": user.role, "company_id": user.company_id})
    return jsonify({"access_token": access, "user": {"id": user.id, "email": user.email, "role":user.role}})

# --------------------
# User management (admin) - create employees/managers
# --------------------
@app.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    """
    Admin endpoint to create user in the same company.
    Body: { name, email, password, role, manager_id (optional), is_manager_approver (optional boolean) }
    """
    cur = get_current_user()
    if cur.role not in ('admin','superadmin'):
        return jsonify({"msg":"admin access required"}), 403
    data = request.json or {}
    name = data.get('name'); email = data.get('email'); password = data.get('password'); role = data.get('role','employee')
    manager_id = data.get('manager_id'); is_manager_approver = data.get('is_manager_approver', False)
    if not (name and email and password):
        return jsonify({"msg":"name,email,password required"}), 400
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(company_id=cur.company_id, name=name, email=email, password_hash=pw_hash, role=role, manager_id=manager_id, is_manager_approver=is_manager_approver)
    db.session.add(user); db.session.commit()
    return jsonify({"msg":"user created", "user_id": user.id}), 201

@app.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    cur = get_current_user()
    if cur.role not in ('admin','superadmin'):
        return jsonify({"msg":"admin access required"}), 403
    users = User.query.filter_by(company_id=cur.company_id).all()
    out = []
    for u in users:
        out.append({"id":u.id,"name":u.name,"email":u.email,"role":u.role,"manager_id":u.manager_id,"is_manager_approver":u.is_manager_approver})
    return jsonify(out)

# --------------------
# Company approvers and rules (admin)
# --------------------
@app.route('/company/approvers', methods=['POST'])
@jwt_required()
def set_company_approvers():
    """
    Set the company approver order. Body: { approver_ids: [3,5,8] } (ordered list)
    Admin only
    """
    cur = get_current_user()
    if cur.role not in ('admin','superadmin'):
        return jsonify({"msg":"admin access required"}), 403
    data = request.json or {}
    ids = data.get('approver_ids', [])
    # remove old
    CompanyApprover.query.filter_by(company_id=cur.company_id).delete()
    db.session.commit()
    # add new in order
    for idx, aid in enumerate(ids, start=1):
        cap = CompanyApprover(company_id=cur.company_id, approver_id=aid, step_order=idx)
        db.session.add(cap)
    db.session.commit()
    return jsonify({"msg":"approver flow set", "count": len(ids)})

@app.route('/company/approval_rule', methods=['POST'])
@jwt_required()
def set_approval_rule():
    """
    Admin sets approval rule. Body: { rule_type: 'percentage'|'specific'|'hybrid', percentage_threshold: 60, specific_approver_id: 5 }
    """
    cur = get_current_user()
    if cur.role not in ('admin','superadmin'):
        return jsonify({"msg":"admin access required"}), 403
    data = request.json or {}
    rtype = data.get('rule_type','percentage'); pct = int(data.get('percentage_threshold',100)); spec = data.get('specific_approver_id')
    rule = ApprovalRule.query.filter_by(company_id=cur.company_id).first()
    if not rule:
        rule = ApprovalRule(company_id=cur.company_id)
    rule.rule_type = rtype
    rule.percentage_threshold = pct
    rule.specific_approver_id = spec
    db.session.add(rule); db.session.commit()
    return jsonify({"msg":"rule updated", "rule": {"type":rule.rule_type,"pct":rule.percentage_threshold,"specific":rule.specific_approver_id}})

# --------------------
# Expense submission & listing
# --------------------
@app.route('/expenses/submit', methods=['POST'])
@jwt_required()
def submit_expense():
    """
    Body: { amount, currency, category, description, expense_date (YYYY-MM-DD) }
    """
    cur = get_current_user()
    data = request.json or {}
    amount = data.get('amount'); currency = data.get('currency','USD'); category = data.get('category'); description = data.get('description'); expense_date = data.get('expense_date')
    if not amount:
        return jsonify({"msg":"amount required"}), 400
    exp = Expense(company_id=cur.company_id, user_id=cur.id, amount=amount, currency=currency, category=category, description=description, expense_date=expense_date)
    db.session.add(exp); db.session.commit()

    # TODO: currency conversion to company currency (call exchangerate-api). For now we keep same.
    exp.amount_in_company_currency = exp.amount
    db.session.add(exp); db.session.commit()

    # create approvals according to company settings
    create_approval_entries_for_expense(exp)
    return jsonify({"msg":"expense submitted", "expense_id": exp.id}), 201

@app.route('/expenses/my', methods=['GET'])
@jwt_required()
def my_expenses():
    cur = get_current_user()
    exps = Expense.query.filter_by(user_id=cur.id).order_by(Expense.created_at.desc()).all()
    out = []
    for e in exps:
        out.append({"id":e.id,"amount":str(e.amount),"currency":e.currency,"status":e.status,"category":e.category,"description":e.description,"date":str(e.expense_date)})
    return jsonify(out)

@app.route('/expenses/all', methods=['GET'])
@jwt_required()
def company_expenses():
    # admin or manager can view
    cur = get_current_user()
    if cur.role not in ('admin','superadmin','manager'):
        return jsonify({"msg":"admin/manager access required"}), 403
    exps = Expense.query.filter_by(company_id=cur.company_id).order_by(Expense.created_at.desc()).all()
    out = []
    for e in exps:
        out.append({"id":e.id,"user_id":e.user_id,"amount":str(e.amount),"currency":e.currency,"status":e.status,"category":e.category})
    return jsonify(out)

# --------------------
# Approvals for approvers (manager / approver)
# --------------------
@app.route('/approvals/pending', methods=['GET'])
@jwt_required()
def pending_approvals():
    cur = get_current_user()
    # list approvals where approver_id == current user and status == 'pending'
    apps = Approval.query.filter_by(approver_id=cur.id, status='pending').all()
    out = []
    for a in apps:
        e = Expense.query.get(a.expense_id)
        out.append({
            "approval_id": a.id,
            "expense_id": e.id,
            "employee_id": e.user_id,
            "amount": str(e.amount),
            "currency": e.currency,
            "category": e.category,
            "description": e.description,
            "expense_date": str(e.expense_date),
            "sequence_order": a.sequence_order
        })
    return jsonify(out)

@app.route('/approvals/<int:approval_id>/decide', methods=['POST'])
@jwt_required()
def decide_approval(approval_id):
    cur = get_current_user()
    app_row = Approval.query.get(approval_id)
    if not app_row or app_row.approver_id != cur.id:
        return jsonify({"msg":"approval not found or not authorized"}), 404
    data = request.json or {}
    action = data.get('action')  # 'approve' or 'reject'
    comment = data.get('comment')
    if action not in ('approve','reject'):
        return jsonify({"msg":"action must be 'approve' or 'reject'"}), 400
    app_row.comment = comment
    app_row.decided_at = datetime.utcnow()
    app_row.status = 'approved' if action=='approve' else 'rejected'
    db.session.add(app_row); db.session.commit()

    expense = Expense.query.get(app_row.expense_id)
    # if this approval was approved and there are waiting approvals -> set next pending
    if app_row.status == 'approved':
        set_next_pending(expense)

    # evaluate finalization based on approval rule
    final = evaluate_expense_post_approval(expense)

    return jsonify({"msg":"decision recorded","final_status": final})

# --------------------
# Utility routes for easy debugging
# --------------------
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"msg":"pong"})

# --------------------
# DB init helper
# --------------------
def create_tables():
    with app.app_context():
        db.create_all()
        # create superadmin if not exists (email: super@admin)
        if not User.query.filter_by(email='super@admin').first():
            pw = bcrypt.generate_password_hash('password').decode('utf-8')
            u = User(name='SuperAdmin', email='super@admin', password_hash=pw, role='superadmin', company_id=None)
            db.session.add(u)
            db.session.commit()


# --- Receipt upload & OCR ---
from werkzeug.utils import secure_filename
import requests
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/receipts/upload', methods=['POST'])
@jwt_required()
def upload_receipt():
    cur = get_current_user()
    if 'file' not in request.files:
        return jsonify({'msg': 'No file part'}), 400
    file = request.files['file']
    expense_id = request.form.get('expense_id')
    if not file or file.filename == '':
        return jsonify({'msg': 'No selected file'}), 400
    if not allowed_file(file.filename):
        return jsonify({'msg': 'Invalid file type'}), 400
    if not expense_id:
        return jsonify({'msg': 'expense_id required'}), 400
    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)
    # OCR stub (replace with real OCR as needed)
    ocr_text = f"[OCR STUB] File {filename} uploaded."
    receipt = Receipt(expense_id=expense_id, file_path=save_path, ocr_text=ocr_text)
    db.session.add(receipt); db.session.commit()
    # Audit log
    log = AuditLog(user_id=cur.id, action='upload_receipt', details=f'Expense {expense_id}, file {filename}')
    db.session.add(log); db.session.commit()
    return jsonify({'msg': 'Receipt uploaded', 'receipt_id': receipt.id, 'ocr_text': ocr_text})

# --- Audit log endpoint (admin) ---
@app.route('/audit/logs', methods=['GET'])
@jwt_required()
def get_audit_logs():
    cur = get_current_user()
    if cur.role not in ('admin','superadmin'):
        return jsonify({'msg': 'admin access required'}), 403
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(100).all()
    out = []
    for l in logs:
        out.append({'id': l.id, 'user_id': l.user_id, 'action': l.action, 'details': l.details, 'created_at': str(l.created_at)})
    return jsonify(out)

# --- Proxy APIs for country/currency info ---
@app.route('/proxy/countries', methods=['GET'])
def proxy_countries():
    url = 'https://restcountries.com/v3.1/all?fields=name,currencies'
    r = requests.get(url)
    return (r.content, r.status_code, r.headers.items())

@app.route('/proxy/exchange/<base>', methods=['GET'])
def proxy_exchange(base):
    url = f'https://api.exchangerate-api.com/v4/latest/{base}'
    r = requests.get(url)
    return (r.content, r.status_code, r.headers.items())


if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT',5000)), debug=True)
