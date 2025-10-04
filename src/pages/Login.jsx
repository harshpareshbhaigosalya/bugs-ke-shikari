import React, {useState} from "react";
import { useNavigate } from "react-router-dom";

export default function Login(){
  const [email,setEmail]=useState('');
  const [password,setPassword]=useState('');
  const [role,setRole]=useState('Employee');
  const navigate = useNavigate();

  function submit(e){
    e.preventDefault();
    alert(`Logged in as ${role} (demo)`);
    navigate('/');
  }

  return (
    <div className="auth-page">
      <div className="container">
        <div className="auth-card">
          <h2>Login</h2>
          <div className="auth-intro">Sign in to your account to manage expenses and approvals.</div>

          <form onSubmit={submit} className="form-grid" style={{alignItems:'center'}}>
            <div className="form-field">
              <label>Email</label>
              <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="Email" required />
            </div>

            <div className="form-field">
              <label>Password</label>
              <input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Enter password" required />
            </div>

            <div className="form-field">
              <label>Role</label>
              <select value={role} onChange={e=>setRole(e.target.value)}>
                <option>Employee</option>
                <option>Manager</option>
                <option>Superadmin</option>
              </select>
            </div>

            <div className="full-row form-actions">
              <button className="btn btn-primary" type="submit">Login</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
