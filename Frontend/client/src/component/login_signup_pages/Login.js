import { Link } from 'react-router-dom';
import './Login.css'

const Login = () => {
    return (
        <div className='login'>
            <input className='input' type="text" placeholder="شماره دانشجویی"></input>
            <input className='input' type="password" placeholder="رمز عبور"></input>
            <button className='button'> ورود </button>
            <div className='option'>
                <Link to="/forgotpassword" className='text'>فراموشی رمز عبور</Link>
                <Link to="/signup" className='text'>ساخت اکانت جدید</Link>
            </div>
        </div>
    );
}

export default Login