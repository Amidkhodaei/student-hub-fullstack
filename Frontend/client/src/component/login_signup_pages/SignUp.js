import './SignUp.css'

const SignUp = () => {
    return (
        <div className='signup'>
            <input className='input' type="text" placeholder="*شماره دانشجویی"></input>
            <input className='input' type="text" placeholder="نام"></input>
            <input className='input' type="text" placeholder="نام خانوادگی"></input>
            <input className='input' type="text" placeholder="شماره"></input>
            <input className='input' type="text" placeholder="*ایمیل"></input>
            <input className='input' type="password" placeholder="*رمز عبور"></input>
            <input className='input' type="password" placeholder="*تکرار رمز عبور"></input>
            <button className='button'> ثبت نام </button>
        </div>
    );
}

export default SignUp