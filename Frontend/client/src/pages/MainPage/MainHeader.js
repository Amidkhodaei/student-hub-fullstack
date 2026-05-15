import { useContext, useState } from 'react';
import './MainHeader.css'
import AuthContext from '../../store/Authentication/AuthContext';

const MainHeader = () => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const authCtx = useContext(AuthContext);
    
    const submithandler = () => {
        authCtx.logout();
    }

    return (
        <div className="header">
            <div className='profile'>
                <img className='picture' src='/profile.png' alt='profile' />
            </div>
            
            {/* دکمه همبرگر برای موبایل */}
            <button 
                className="hamburger" 
                onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
                ☰
            </button>
            
            <div className={`menu ${isMenuOpen ? 'open' : ''}`}>
                <nav className='navbar'> 
                    <ul>
                        
                        <li><a href='/comments'>نظرات و پیشنهادات</a></li>
                        <li><a href='/survey'>نظرسنجی اساتید</a></li>
                        <li><a href='/terminder'>ترمایندر</a></li>
                        <li><a href='/dashboard' className='home_link'>خانه</a></li>
                    </ul>
                </nav>
            </div>
        </div>
    );
};

export default MainHeader