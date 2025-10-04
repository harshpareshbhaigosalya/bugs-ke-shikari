import React, {useState} from "react";
import { useNavigate } from "react-router-dom";

export default function Register(){
  const [name,setName]=useState('');
  const [email,setEmail]=useState('');
  const [password,setPassword]=useState('');
  const [role,setRole]=useState('Employee');
  const navigate = useNavigate();

  function submit(e){
    e.preventDefault();
    alert(`Registered ${name} as ${role} (demo)`);
    navigate('/login');
  }

  return (
    <div className="auth-page">
      <div className="container">
        <div className="auth-card">
          <h2>Create an account</h2>
          <div className="auth-intro">Create a user account. Choose your role — Employee, Manager, or Superadmin.</div>

          <form onSubmit={submit} className="form-grid">
            <div className="form-field">
              <label>Full name</label>
              <input value={name} onChange={e=>setName(e.target.value)} placeholder="name" required />
            </div>

            <div className="form-field">
              <label>Email</label>
              <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="Email" required />
            </div>

            <div className="form-field">
              <label>Password</label>
              <input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Choose a password" required />
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
              <button className="btn btn-primary" type="submit">Register</button>
              <button type="button" className="btn" onClick={()=>navigate('/company-register')}>Register Company</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
