import React from "react";
import HeroImage from "../assets/hero-placeholder.jpg"; // put your hero image in src/assets

export default function Home(){
  return (
    <div>
      <div className="container hero">
        <div className="hero-inner">
          <div className="hero-left">
            <h1 className="headline">Streamline Your Employee Management & Expense Tracking</h1>
            <p className="lead">Complete solution for employee management, expense approvals, and workflow automation — built for modern teams.</p>
            <div className="hero-cta">
              <a className="btn btn-primary" href="/register">Get Started</a>
              <a className="btn" href="#features">View Demo</a>
            </div>
          </div>

          <div className="hero-right">
            <div className="hero-visual" aria-hidden>
              <img src={HeroImage} alt="dashboard preview" />
            </div>
          </div>
        </div>

        {/* Features placed below hero (ensures they sit under the hero image) */}
        <div id="features" className="section">
          <h3 className="section-title">Key Features</h3>
          <div className="features">
            <div className="feature-card">
              <h3>Smart Role Management</h3>
              <p>Admin and employee dashboards with custom access and permissions, manager assignments and secure controls.</p>
            </div>
            <div className="feature-card">
              <h3>Effortless Expense Tracking</h3>
              <p>Submit, track, and approve expenses with complete audit trails and receipt attachments.</p>
            </div>
            <div className="feature-card">
              <h3>Complete Employee Management</h3>
              <p>Manage teams, reporting relationships and employee data, with easy import/export and reporting.</p>
            </div>
          </div>
        </div>

        {/* stepper */}
        <div style={{marginTop:22}}>
          <div className="stepper">
            <div className="step">
              <div className="circle">1</div>
              <div className="step-title">Register</div>
              <div className="step-sub">Create account & company</div>
            </div>
            <div className="step">
              <div className="circle">2</div>
              <div className="step-title">Manage</div>
              <div className="step-sub">Add roles & teams</div>
            </div>
            <div className="step">
              <div className="circle">3</div>
              <div className="step-title">Submit</div>
              <div className="step-sub">Employees submit expenses</div>
            </div>
            <div className="step">
              <div className="circle">4</div>
              <div className="step-title">Approve</div>
              <div className="step-sub">Multi-level approvals</div>
            </div>
            <div className="step">
              <div className="circle">5</div>
              <div className="step-title">Track</div>
              <div className="step-sub">Reports & audit trails</div>
            </div>
          </div>
        </div>

        {/* Dashboards preview */}
        <section className="section" style={{marginTop:26}}>
          <h3 className="section-title">Tailored Dashboards for Every Role</h3>
          <div className="cards-row">
            <div className="preview-card">
              <h4>Admin Dashboard</h4>
              <div className="preview-stats">
                <div className="stat"><strong>248</strong><small>Active users</small></div>
                <div className="stat"><strong>12</strong><small>Pending</small></div>
                <div className="stat"><strong>$45K</strong><small>Monthly</small></div>
              </div>
              <p style={{color:"#6b7280",marginTop:6}}>Quick actions: Add employee • View reports</p>
            </div>

            <div className="preview-card">
              <h4>Employee Dashboard</h4>
              <div className="preview-stats">
                <div className="stat"><strong>8</strong><small>My expenses</small></div>
                <div className="stat"><strong>5</strong><small>Approved</small></div>
                <div className="stat"><strong>3</strong><small>Pending</small></div>
              </div>
              <p style={{color:"#6b7280",marginTop:6}}>Recent: Office supplies • Taxi • Lunch</p>
            </div>
          </div>
        </section>

        {/* tech & footer simplified
        <section className="section" style={{textAlign:'center', marginTop:28}}>
          <h3 className="section-title">Built with Modern Technology</h3>
          <div className="tech-grid" style={{marginTop:12}}>
            <div className="tech-item"><svg width="28" height="28" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="#2b6cff" strokeWidth="1.6"/></svg><small>React</small></div>
            <div className="tech-item"><svg width="28" height="28" viewBox="0 0 24 24" fill="none"><rect x="3" y="3" width="18" height="18" rx="3" stroke="#0fb6ff" strokeWidth="1.6"/></svg><small>Flask</small></div>
            
            <div className="tech-item"><svg width="28" height="28" viewBox="0 0 24 24" fill="none"><rect x="4" y="4" width="16" height="16" rx="2" stroke="#0b9a66" strokeWidth="1.6"/></svg><small>MySQL</small></div>
          </div>
        </section> */}

        <footer className="footer" style={{marginTop:32}}>
          <div className="container footer-grid" style={{paddingLeft:0,paddingRight:0}}>
            <div>
              <strong>Expense Flow</strong>
              <div style={{marginTop:8,color:"rgba(255,255,255,0.9)"}}>Modern employee management and expense tracking.</div>
            </div>
            <div style={{textAlign:'right'}}>
              <small>© {new Date().getFullYear()} Expense Flow . All rights reserved.</small>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
