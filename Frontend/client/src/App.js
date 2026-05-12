//import logo from './logo.svg';
import './App.css';
import { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AuthContext from '../src/store/Authentication/AuthContext'
import Login from './pages/login_signup_pages/Login'
import SignUp from './pages/login_signup_pages/SignUp'
import ForgotPassword from './pages/login_signup_pages/ForgotPassword';
import MainPage from './pages/MainPage/MainPage';
import MainHeader from './pages/MainPage/MainHeader';

function App() {
  const authCtx = useContext(AuthContext);

  return (
    <Router>
      <div className="app-container">
        {authCtx.isLoggedIn && 
          <div className='fixed_header'>
            <MainHeader></MainHeader>
          </div>
        }
        <div className='APP'>
          <Routes>
            <Route path='/' element={<Navigate to="/login" />} />
            {!authCtx.isLoggedIn &&
              <Route path='/login' element={<Login />} /> }
            {!authCtx.isLoggedIn &&
              <Route path='/signup' element={<SignUp />} />}
            {!authCtx.isLoggedIn &&
              <Route path='/forgotpassword' element={<ForgotPassword />} />}

            {authCtx.isLoggedIn &&
              <Route path='/login' element={<Navigate to="/dashboard" />} /> }
            {authCtx.isLoggedIn &&
              <Route path='/signup' element={<Navigate to="/dashboard"/>} />}
            {authCtx.isLoggedIn &&
              <Route path='/forgotpassword' element={<Navigate to="/dashboard"/>} />}
            
            {authCtx.isLoggedIn && <Route path='/dashboard' element={<MainPage />} />}
            {!authCtx.isLoggedIn && <Route path='/dashboard' element={<Navigate to="/login" />} />}
          </Routes>
          <p className='Made'>
            Made By <span className='quaalla'>Quaalla</span>
          </p>
        </div>
      </div>
    </Router>
  );
}

export default App;
