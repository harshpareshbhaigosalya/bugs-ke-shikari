import React from 'react'
import { Routes, Route } from 'react-router-dom'
import NavBar from './components/NavBar'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import CompanyRegister from './pages/CompanyRegister'

export default function App(){
  return (
    <div className='app-root'>
      <NavBar />
      <main style={{paddingTop: '80px'}}>
        <Routes>
          <Route path='/' element={<Home/>} />
          <Route path='/login' element={<Login/>} />
          <Route path='/register' element={<Register/>} />
          <Route path='/company-register' element={<CompanyRegister/>} />
        </Routes>
      </main>
    </div>
  )
}
