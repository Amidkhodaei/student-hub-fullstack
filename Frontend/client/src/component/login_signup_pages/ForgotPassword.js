import './ForgotPassword.css'

const ForgotPassword = () => {
    return (
        <div className='forgot_Password'>
            <input className='input' type="text" placeholder="شماره دانشجویی"></input>
            <input className='input' type="text" placeholder="ایمیل"></input>
            <input className='input' type="password" placeholder="رمز عبور جدید"></input>
            <input className='input' type="password" placeholder=" تکرار رمز عبور جدید"></input>
            <button className='button'> تغییر رمز عبور </button>
        </div>
    );
}

export default ForgotPassword