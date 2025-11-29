import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
// import './App.css'
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Analytics from './pages/Analytics';
import Contact from './pages/Contact';
import About from './pages/About';
import Home from './pages/Home';

function App() {

  return (
    <>
      <Router>
        <div className="App">
        <Navbar/>
          <div className="content mt-21">
            <Routes>
              <Route path='/' element={<Home/>}/>
              <Route path='/analytics' element={<Analytics/>}/>
              <Route path='/about' element={<About/>}/>
              <Route path='/contact' element={<Contact/>}/>
            </Routes>
          </div>
        <Footer/>
        </div>
      </Router>
      
      
    </>
  )
}

export default App;
