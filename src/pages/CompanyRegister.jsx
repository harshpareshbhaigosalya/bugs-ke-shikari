import React, {useState} from "react";
import { useNavigate } from "react-router-dom";

export default function CompanyRegister(){
  const [name,setName]=useState('');
  const [email,setEmail]=useState('');
  const [country,setCountry]=useState('');
  const [currency,setCurrency]=useState('USD');
  const navigate = useNavigate();

  function submit(e){
    e.preventDefault();
    alert(`Company ${name} registered (demo)`);
    navigate('/register');
  }

  return (
    <div className="auth-page">
      <div className="container">
        <div className="auth-card">
          <h2>Register Company</h2>
          <div className="auth-intro">Create your company profile and admin account. You can add employees later.</div>

          <form onSubmit={submit} className="form-grid">
            <div className="form-field">
              <label>Company Name</label>
              <input value={name} onChange={e=>setName(e.target.value)} placeholder="comapny name." required />
            </div>

            <div className="form-field">
              <label>Admin Email</label>
              <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="email" required />
            </div>

            <div className="form-field">
              <label>Country</label>
              <input value={country} onChange={e=>setCountry(e.target.value)} placeholder="United States,etc" />
            </div>

            <div className="form-field">
              <label>Default Currency</label>
              <select value={currency} onChange={e=>setCurrency(e.target.value)}>
                <option>USD</option>
                <option>EUR</option>
                <option>INR</option>
                <option>GBP</option>
                <option>AUD</option>
              </select>
            </div>

            <div className="full-row form-actions">
              <button className="btn btn-primary" type="submit">Create Company</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
