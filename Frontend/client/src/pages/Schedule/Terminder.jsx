import { useState, useEffect, useContext } from 'react';
import AuthContext from '../../store/Authentication/AuthContext';
import ToastContext from '../../store/Toast/ToastContext';
import WeekSchedule from './WeekSchedule';
import LessonSelectList from './LessonSelectList';
import './Terminder.css';

const LAB_PREFIXES = ['آزمایشگاه', 'ازمايشگاه', 'آزمايشگاه', 'كارگاه', 'کارگاه'];

const isLabOrWorkshop = (lessonName) => LAB_PREFIXES.some((prefix) => lessonName.startsWith(prefix));

const Terminder = () => {
    const authCtx = useContext(AuthContext);
    const { showToast } = useContext(ToastContext);

    const [departments, setDepartments] = useState([]);
    const [selectedDeptId, setSelectedDeptId] = useState('');
    const [deptLessons, setDeptLessons] = useState([]);
    const [loadingLessons, setLoadingLessons] = useState(false);

    // دروس انتخاب‌شده‌ی کاربر برای چارت: [{ lesson, color }]
    const [scheduleItems, setScheduleItems] = useState([]);

    useEffect(() => {
        const fetchDepartments = async () => {
            try {
                const response = await fetch('http://127.0.0.1:8000/api/department/', {
                    headers: { Authorization: `Bearer ${authCtx.access}` },
                });
                const data = await response.json();
                if (!response.ok) throw new Error('خطا در دریافت دانشکده‌ها');
                setDepartments(data);
            } catch (error) {
                showToast('خطا در دریافت لیست دانشکده‌ها', 'error');
            }
        };
        fetchDepartments();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    useEffect(() => {
        if (!selectedDeptId) {
            setDeptLessons([]);
            return;
        }
        const fetchLessons = async () => {
            setLoadingLessons(true);
            try {
                const response = await fetch(
                    `http://127.0.0.1:8000/api/lessons/?department_id=${selectedDeptId}`,
                    { headers: { Authorization: `Bearer ${authCtx.access}` } }
                );
                const data = await response.json();
                if (!response.ok) throw new Error('خطا در دریافت دروس');
                setDeptLessons(data);
            } catch (error) {
                showToast('خطا در دریافت لیست دروس این دانشکده', 'error');
            } finally {
                setLoadingLessons(false);
            }
        };
        fetchLessons();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selectedDeptId]);

    const theoryLessons = deptLessons.filter((l) => !isLabOrWorkshop(l.lesson_name));
    const labLessons = deptLessons.filter((l) => isLabOrWorkshop(l.lesson_name));

    const handleSelectLesson = (lesson) => {
        const isAlreadyAdded = scheduleItems.some((item) => item.lesson.id === lesson.id);
        if (isAlreadyAdded) {
            showToast('.این درس قبلاً به برنامه اضافه شده است', 'error');
            return;
        }
        setScheduleItems((prev) => [...prev, { lesson, color: '#2BCDE2' }]);
        showToast(`درس «${lesson.lesson_name}» .اضافه شد`, 'success');
    };

    const handleDeleteLesson = (lessonPk) => {
        setScheduleItems((prev) => prev.filter((item) => item.lesson.id !== lessonPk));
    };

    const totalCredit = scheduleItems.reduce((sum, item) => sum + (item.lesson.credit || 0), 0);

    return (
        <div className='terminder_page'>
            <WeekSchedule
                items={scheduleItems}
                onDelete={handleDeleteLesson}
                onLessonClick={() => {}}
            />

            <div className='terminder_summary'>
                <span>مجموع واحدها: {totalCredit}</span>
            </div>

            <div className='terminder_controls'>
                <select
                    className='terminder_dept_select'
                    value={selectedDeptId}
                    onChange={(e) => setSelectedDeptId(e.target.value)}
                >
                    <option value=''>انتخاب دانشکده</option>
                    {departments.map((dept) => (
                        <option key={dept.dept_id} value={dept.dept_id}>
                            {dept.dept_name}
                        </option>
                    ))}
                </select>

                <div className='terminder_lesson_lists'>
                    <LessonSelectList
                        title='دروس تئوری'
                        lessons={theoryLessons}
                        onSelect={handleSelectLesson}
                        disabled={!selectedDeptId || loadingLessons}
                        disabledMessage={!selectedDeptId ? 'ابتدا دانشکده را انتخاب کنید' : '...در حال بارگذاری'}
                    />
                    <LessonSelectList
                        title='آزمایشگاه و کارگاه'
                        lessons={labLessons}
                        onSelect={handleSelectLesson}
                        disabled={!selectedDeptId || loadingLessons}
                        disabledMessage={!selectedDeptId ? 'ابتدا دانشکده را انتخاب کنید' : '...در حال بارگذاری'}
                    />
                </div>
            </div>
        </div>
    );
};

export default Terminder;
