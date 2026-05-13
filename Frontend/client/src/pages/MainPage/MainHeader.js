import { useContext } from 'react';
import './MainHeader.css'
import AuthContext from '../../store/Authentication/AuthContext';

const MainHeader = () => {
    const authCtx = useContext(AuthContext);
    
    const submithandler = () => {
        authCtx.logout();
    }

    return (
        <div className="header">
            <div className='profile'>
                <img className='picture' src='/profile.png' />
            </div>
            <div className='menu'>
                <nav className='navbar'> 
                    <ul>
                        <li>
                            <a href='/Comments'>نظرات و پیشنهادات</a>
                        </li>
                        <li>
                            <a href='/survey'>نظرسنجی اساتید</a>
                        </li>
                        <li>
                            <a href='/terminder'>ترمایندر</a>
                        </li>
                        <li>
                            <a href='/dashboard' className='home_link'>خانه</a>
                        </li>
                        
                    </ul>
                </nav>
            </div>
        </div>
    );
};

export default MainHeader