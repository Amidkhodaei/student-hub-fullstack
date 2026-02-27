import logo from './logo.svg';
import './App.css';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './component/login_signup_pages/Login'
import SignUp from './component/login_signup_pages/SignUp'
import ForgotPassword from './component/login_signup_pages/ForgotPassword';

function App() {
  return (
    <Router>
      <div className='APP'>
        <Routes>
          <Route path='/' element={<Navigate to="/login" />} />
          <Route path='/login' element={<Login />} />
          <Route path='/signup' element={<SignUp />} />
          <Route path='/forgotpassword' element={<ForgotPassword />} />
        </Routes>

        <p className='Made'>Made By <span className='quaalla'>Quaalla</span></p>
      </div>
    </Router>
  );
}

export default App;
