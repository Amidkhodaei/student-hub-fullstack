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
            <div className='menu'></div>
        </div>
    );
};

export default MainHeader