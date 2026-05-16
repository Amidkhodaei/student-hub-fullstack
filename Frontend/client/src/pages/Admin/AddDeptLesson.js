import {useState, useContext, useEffect} from 'react'
import './AddDeptLesson.css'
import InputBox from '../../component/input_box/InputBox';
import AuthContext from '../../store/Authentication/AuthContext';

const AddDeptLesson = () => {
    const authCtx = useContext(AuthContext);
    const [deptid, setDeptid] = useState('00');
    const [deptname, setDeptname] = useState([]);
    const [departments, setDepartments] = useState(null);
    const [counter, setCounter] = useState(0);
    const [selectedDept, setSelectedDept] = useState('');

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
            setCounter(counter+1);
        } catch(error) {
            console.error('invalid:', error);
        }
        return;
    };

    useEffect(() => {
        const fetchDepartments = async () => {
            try {
                const response = await fetch('http://127.0.0.1:8000/api/department/', {
                    method: 'GET',
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${authCtx.access}`
                    },
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error('sth went wrong!');
                }

                setDepartments(data);
                console.log(data);
                
            } catch(error) {
                console.error('invalid:', error);
            }
        };
        
        fetchDepartments();
    }, [counter]);

    const handleDeptChange = (event) => {
        setSelectedDept(event.target.value);
        console.log('Department selected:', event.target.value);
    };

    return (
        <div>
            <div className='AddBox'>
                <InputBox type="text" value={deptid} onChange={changeidhandler} isValid={true} defualt='10' style={{ width: '15%', height: '50px', fontSize: '1.2rem' }}></InputBox>
                <InputBox type="text" value={deptname} onChange={changenamehadndler} isValid={true} defualt='مهندسی کامپیتر' style={{ width: '55%', height: '50px', fontSize: '1.2rem' }}></InputBox>
                <button className='SubmitBox' onClick={addDeptbutton}>Add Department</button>
            </div>

            <div className='AddBox'>
                <select 
                    value={selectedDept} 
                    onChange={handleDeptChange}
                    className='SelectBox'
                >
                    <option value=""> -- Department -- </option>
                    {departments && departments.length > 0 ? (
                        departments.map((dept) => (
                            <option key={dept.id} value={dept.id}>
                                {dept.dept_name}
                            </option>
                        ))
                    ) : (
                        <option disabled>هیچ دپارتمانی یافت نشد</option>
                    )}
                </select>
            </div>
        </div>
    );
};

export default AddDeptLesson