import {useState, useContext} from 'react'
import './AddDeptLesson.css'
import InputBox from '../../component/input_box/InputBox';
import AuthContext from '../../store/Authentication/AuthContext';

const AddDeptLesson = () => {
    const authCtx = useContext(AuthContext);
    const [deptid, setDeptid] = useState('00');
    const [deptname, setDeptname] = useState('');

    const changeidhandler = (event) => {
        setDeptid(event.target.value.trim());
    };

    const changenamehadndler = (event) => {
        setDeptname(event.target.value.trim());
    };

    const addDeptbutton = async () => {
        if (deptid.length != 2) return;
        if (deptname.length == 0) return;

        console.log(deptid + ' ' + deptname);

        try{
            const respone = await fetch('http://127.0.0.1:8000/api/department/', {
                method:'POST',
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${authCtx.access}`
                },
                body: JSON.stringify({
                    dept_id: parseInt(deptid),
                    dept_name: deptname
                }),
            });
            const data = await respone.json()
            
            if (!respone.ok) {
                throw new Error('sth went wrong!');
            }

            console.log('valid');
        } catch(error) {
            console.error('invalid:', error);
        }
        return;
    };

    return (
        <div>
            <div className='AddBox'>
                <InputBox type="text" value={deptid} onChange={changeidhandler} isValid={true} defualt='10' style={{ width: '15%', height: '50px', fontSize: '1.2rem' }}></InputBox>
                <InputBox type="text" value={deptname} onChange={changenamehadndler} isValid={true} defualt='مهندسی کامپیتر' style={{ width: '55%', height: '50px', fontSize: '1.2rem' }}></InputBox>
                <button className='SubmitBox' onClick={addDeptbutton}>Add Department</button>
            </div>
        </div>
    );
};

export default AddDeptLesson