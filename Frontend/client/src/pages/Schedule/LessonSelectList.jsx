import { useState } from 'react';

const LessonSelectList = ({ title, lessons, onSelect, disabled, disabledMessage }) => {
    const [search, setSearch] = useState('');

    const filtered = lessons.filter((lesson) => {
        const q = search.trim().toLowerCase();
        if (!q) return true;
        return (
            lesson.lesson_name.toLowerCase().includes(q) ||
            lesson.lesson_id.toLowerCase().includes(q) ||
            (lesson.instructors_list || []).some((i) => i.toLowerCase().includes(q))
        );
    });

    return (
        <div className='lesson_select_box'>
            <p className='lesson_select_title'>{title}</p>
            <input
                type='text'
                className='lesson_select_search'
                placeholder='جستجوی نام درس، استاد یا کد درس...'
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                disabled={disabled}
                dir='rtl'
            />
            {disabled ? (
                <p className='lesson_select_empty'>{disabledMessage}</p>
            ) : (
                <div className='lesson_select_list'>
                    {filtered.length === 0 && <p className='lesson_select_empty'>موردی یافت نشد</p>}
                    {filtered.map((lesson) => (
                        <div key={lesson.id} className='lesson_select_item' onClick={() => onSelect(lesson)}>
                            <span className='lesson_select_item_name'>{lesson.lesson_name}</span>
                            <span className='lesson_select_item_meta'>
                                {(lesson.instructors_list || []).join('، ')}
                                {lesson.instructors_list?.length > 0 && ' — '}
                                {lesson.lesson_id}
                            </span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default LessonSelectList;
