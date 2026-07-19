import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const VerifyEmail = () => {
    const { uidb64, token } = useParams();
    const navigate = useNavigate();
    const [status, setStatus] = useState('loading'); // loading, success, error
    const [message, setMessage] = useState('در حال بررسی و فعال‌سازی حساب کاربری...');

    useEffect(() => {
        const verifyAccount = async () => {
            try {
                const response = await axios.post(`http://127.0.0.1:8000/api/users/verify-email/${uidb64}/${token}/`);
                setStatus('success');
                setMessage(response.data.message || 'حساب کاربری شما با موفقیت فعال شد!');
            } catch (error) {
                setStatus('error');
                if (error.response && error.response.data) {
                    setMessage(error.response.data.error || error.response.data.message || 'لینک تایید نامعتبر یا منقضی شده است.');
                } else {
                    setMessage('ارتباط با سرور برقرار نشد. لطفاً مجدداً تلاش کنید.');
                }
            }
        };

        if (uidb64 && token) {
            verifyAccount();
        }
    }, [uidb64, token]);

    return (
        <div style={styles.container}>
            {/* اضافه کردن تگ استایل برای انیمیشن لودینگ */}
            <style>{`
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `}</style>

            <div style={styles.card}>
                {status === 'loading' && <div style={styles.spinner}>🔄</div>}
                {status === 'success' && <div style={styles.successIcon}>✅</div>}
                {status === 'error' && <div style={styles.errorIcon}>❌</div>}
                
                <p style={styles.text}>{message}</p>

                {status !== 'loading' && (
                    <button style={styles.button} onClick={() => navigate('/login')}>
                        ورود به سامانه
                    </button>
                )}
            </div>
        </div>
    );
};

const styles = {
    container: { 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh', 
        width: '100vw',
        backgroundColor: '#0a192f', // تم سرمه‌ای تیره هماهنگ با پس‌زمینه شما
        direction: 'rtl',
        margin: 0,
        padding: 0,
        overflow: 'hidden'
    },
    card: { 
        padding: '40px 30px', 
        borderRadius: '16px', 
        backgroundColor: '#ffffff', 
        boxShadow: '0 10px 25px rgba(0, 0, 0, 0.3)', 
        textAlign: 'center', 
        maxWidth: '380px', 
        width: '90%', // ریسپانسیو برای موبایل
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '15px'
    },
    text: { 
        fontSize: '16px', 
        fontWeight: '500',
        color: '#333333', 
        margin: '10px 0 20px 0', 
        lineHeight: '1.7' 
    },
    spinner: { 
        fontSize: '45px', 
        animation: 'spin 1.5s linear infinite',
        display: 'inline-block'
    },
    successIcon: { 
        fontSize: '55px', 
        color: '#28a745',
        filter: 'drop-shadow(0px 4px 8px rgba(40, 167, 69, 0.2))'
    },
    errorIcon: { 
        fontSize: '55px', 
        color: '#dc3545',
        filter: 'drop-shadow(0px 4px 8px rgba(220, 53, 69, 0.2))'
    },
    button: { 
        padding: '12px 28px', 
        backgroundColor: '#007bff', 
        color: '#ffffff', 
        border: 'none', 
        borderRadius: '8px', 
        cursor: 'pointer', 
        fontSize: '15px', 
        fontWeight: 'bold',
        width: '100%',
        transition: 'all 0.2s ease',
        boxShadow: '0 4px 12px rgba(0, 123, 255, 0.3)'
    }
};

export default VerifyEmail;