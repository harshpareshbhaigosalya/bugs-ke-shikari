import React from "react";
import { Link, useLocation } from "react-router-dom";
import "../styles.css";

export default function NavBar(){
  const loc = useLocation();
  return (
    <header className="nav container" style={{paddingLeft:0,paddingRight:0}}>
      <div style={{display:'flex',alignItems:'center',gap:12}}>
        <Link to="/" className="brand" style={{textDecoration:'none'}}>
          <svg width="34" height="34" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="1" y="1" width="22" height="22" rx="6" fill="#2b6cff" opacity="0.12"/>
            <path d="M6 8h12M6 12h12M6 16h12" stroke="#2b6cff" strokeWidth="1.6" strokeLinecap="round"/>
          </svg>
          <span className="brand-text" style={{marginLeft:8,fontWeight:700,color:'#071330'}}>Expense Flow</span>
        </Link>
      </div>

      <nav className="nav-right">
        <Link className="nav-link" to="/">Home</Link>
        <Link className="nav-link" to="/login">Login</Link>
        <Link to="/register" className="btn btn-ghost">Sign Up</Link>
      </nav>
    </header>
  );
}
