import InputBox from '../../component/input_box/InputBox';
import React, {useState} from 'react';
import { Link } from 'react-router-dom';
import './ForgotPassword.css'

const ForgotPassword = () => {
    const [forgotPassInput, setForgotPassInput] = useState({
            enteredStudentNo: '',
            enteredFirstName: '',
            enteredLastName: '',
            enteredPhone: '',
            enteredEmail: '',
            enteredPass1: '',
            enteredPass2: ''
        });

    const [isValidInput, setIsValidInput] = useState({
            isValidStudentNo: true,
            isValidEmail: true,
            isValidPass1: true,
            isValidPass2: true,
        });
    
    const studentnochangehandler = (event) => {
        if (event.target.value.trim().length > 0) {
            setIsValidInput((prevState) => {
                return {...prevState, isValidStudentNo: true}
            })
        }
        setForgotPassInput((prevState) => {
            return {...prevState, enteredStudentNo: event.target.value};
        });
    }

    const emailchangehandler = (event) => {
        if (event.target.value.trim().length > 0) {
            setIsValidInput((prevState) => {
                return {...prevState, isValidEmail: true}
            })
        }
        setForgotPassInput((prevState) => {
            return {...prevState, enteredEmail: event.target.value}
        })
    }

    const pass1changehandler = (event) => {
        if (event.target.value.trim().length > 0) {
            setIsValidInput((prevState) => {
                return {...prevState, isValidPass1: true}
            })
        }
        setForgotPassInput((prevState) => {
            return {...prevState, enteredPass1: event.target.value}
        })
    }

    const pass2changehandler = (event) => {
        if (event.target.value.trim().length > 0) {
            setIsValidInput((prevState) => {
                return {...prevState, isValidPass2: true}
            })
        }
        setForgotPassInput((prevState) => {
            return {...prevState, enteredPass2: event.target.value}
        })
    }
    
    const submithandler = (event) => {
        event.preventDefault()

        if (forgotPassInput.enteredStudentNo.trim().length === 0) {
            setIsValidInput((prevState) => {
                return {...prevState, isValidStudentNo: false}
            })
        } else {
            setIsValidInput((prevState) => {
                return {...prevState, isValidStudentNo: true}
            })
        }

        if (forgotPassInput.enteredEmail.trim().length === 0) {
            setIsValidInput((prevState) => {
                return {...prevState, isValidEmail: false}
            })
        } else {
            setIsValidInput((prevState) => {
                return {...prevState, isValidEmail: true}
            })
        }

        if (forgotPassInput.enteredPass1.trim().length === 0) {
            setIsValidInput((prevState) => {
                return {...prevState, isValidPass1: false}
            })
        } else {
            setIsValidInput((prevState) => {
                return {...prevState, isValidPass1: true}
            })
        }

        if (forgotPassInput.enteredPass2.trim().length === 0) {
            setIsValidInput((prevState) => {
                return {...prevState, isValidPass2: false}
            })
        } else {
            setIsValidInput((prevState) => {
                return {...prevState, isValidPass2: true}
            })
        }
    }

    return (
        <div className='forgot_Password'>
            <InputBox type="text" value={forgotPassInput.enteredStudentNo} onChange={studentnochangehandler} isValid={isValidInput.isValidStudentNo} defualt='شماره دانشجویی' />
            <InputBox type="text" value={forgotPassInput.enteredEmail}     onChange={emailchangehandler}     isValid={isValidInput.isValidEmail} defualt='ایمیل' />
            <InputBox type="password" value={forgotPassInput.enteredPass1} onChange={pass1changehandler}     isValid={isValidInput.isValidPass1} defualt='رمز عبور جدید' />
            <InputBox type="password" value={forgotPassInput.enteredPass2} onChange={pass2changehandler}     isValid={isValidInput.isValidPass2} defualt='تکرار رمز عبور جدید' />
            <button className='button' onClick={submithandler}> تغییر رمز عبور </button>
            <Link to="/login" className='text'>حساب کاربری دارید؟</Link>
        </div>
    );
}

export default ForgotPassword