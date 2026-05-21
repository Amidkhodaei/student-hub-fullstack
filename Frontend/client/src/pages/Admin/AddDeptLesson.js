import {useState, useContext, useEffect, useRef} from 'react'
import './AddDeptLesson.css'
import InputBox from '../../component/input_box/InputBox';
import AuthContext from '../../store/Authentication/AuthContext';
import ButtonBox from '../../component/button/ButtonBox';

const AddDeptLesson = () => {
    const authCtx = useContext(AuthContext);
    const [deptid, setDeptid] = useState('00');
    const [deptname, setDeptname] = useState([]);
    const [departments, setDepartments] = useState(null);
    const [counter, setCounter] = useState(0);
    const [selectedDept, setSelectedDept] = useState('');
    const [excelFile, setExcelFile] = useState(null);
    const [sendingFile, setSendingFile] = useState(false);
    const fileInputRef = useRef(null);

    const changeidhandler = (event) => {
        setDeptid(event.target.value.trim());
    };

    const changenamehadndler = (event) => {
        setDeptname(event.target.value.trim());
    };

    const addDeptbutton = async () => {
        if (deptid.length !== 2) return;
        if (deptname.length === 0) return;

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

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file && (file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || 
                     file.type === 'application/vnd.ms-excel')) {
            setExcelFile(file);
        } else {
            setExcelFile(null);
        }
    };

    const handlefileSubmit = async () => {
        if (!selectedDept) return;
        
        if (!excelFile) return;

        setSendingFile(true);

        // ایجاد FormData برای ارسال فایل
        const formData = new FormData();
        formData.append('department_id', selectedDept);
        formData.append('excel_file', excelFile);

        try {
            const response = await fetch('http://127.0.0.1:8000/api/upload-lessons/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${authCtx.access}`,
                },
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                console.log(data)
                throw new Error(data.error || data.message || 'خطا در آپلود فایل');
            }

            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }

            console.log(data);

            setExcelFile(null);
            
        } catch (error) {
             console.error('invalid:', error);
        } finally {
            setSendingFile(false);
        }
    };

    return (
        <div>
            <div className='AddBox'>
                <InputBox type="text" value={deptid} onChange={changeidhandler} isValid={true} defualt='10' style={{ width: '15%', height: '50px', fontSize: '1.2rem' }}></InputBox>
                <InputBox type="text" value={deptname} onChange={changenamehadndler} isValid={true} defualt='مهندسی کامپیتر' style={{ width: '55%', height: '50px', fontSize: '1.2rem' }}></InputBox>
                <ButtonBox onClick={addDeptbutton} defualt='Add Department' loading={false}></ButtonBox>
            </div>

            <div className='AddBox'>
                <InputBox type='file' ref={fileInputRef} value='addfile' onChange={handleFileChange} isValid={true} style={{ width: '40%', height: '28px' }}></InputBox>

                <select 
                    value={selectedDept} 
                    onChange={handleDeptChange}
                    className='SelectBox'
                >
                    <option value=""> -- Department -- </option>
                    {departments && departments.length > 0 ? (
                        departments.map((dept) => (
                            <option key={dept.dept_id} value={dept.dept_id}>
                                {dept.dept_name}
                            </option>
                        ))
                    ) : (
                        <option disabled>هیچ دپارتمانی یافت نشد</option>
                    )}
                </select>

                <ButtonBox onClick={handlefileSubmit} defualt='Add Lessons' loading={sendingFile} style={{width: '30%', height: '50px'}}></ButtonBox>
            </div>
        </div>
    );
};

export default AddDeptLesson