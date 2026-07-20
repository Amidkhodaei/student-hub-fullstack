export const WEEK_DAYS = [
    { key: 0, label: 'شنبه' },
    { key: 1, label: 'یکشنبه' },
    { key: 2, label: 'دوشنبه' },
    { key: 3, label: 'سه‌شنبه' },
    { key: 4, label: 'چهارشنبه' },
];

export const START_HOUR = 8;
export const END_HOUR = 17;
export const SLOT_MINUTES = 30;
export const SLOTS_COUNT = ((END_HOUR - START_HOUR) * 60) / SLOT_MINUTES; 


export const getTimeLabels = () => {
    const labels = [];
    for (let i = 0; i <= SLOTS_COUNT; i++) {
        const totalMinutes = START_HOUR * 60 + i * SLOT_MINUTES;
        const hour = Math.floor(totalMinutes / 60);
        const minute = totalMinutes % 60;
        labels.push(minute === 0 ? `${hour}` : `${hour}:${minute}`);
    }
    return labels;
};


export const timeStringToMinutes = (timeStr) => {
    if (!timeStr || typeof timeStr !== 'string' || !timeStr.includes(':')) return null;
    const [h, m] = timeStr.split(':').map(Number);
    if (Number.isNaN(h) || Number.isNaN(m)) return null;
    return h * 60 + m;
};


export const timeToSlotIndex = (timeStr) => {
    const minutes = timeStringToMinutes(timeStr);
    if (minutes === null) return null;
    const startMinutes = START_HOUR * 60;
    const index = (minutes - startMinutes) / SLOT_MINUTES;
    return index;
};


export const timesOverlap = (time1, time2) => {
    if (time1.day !== time2.day) return false;
    if (time1.isExerciseSolving || time2.isExerciseSolving) return false;

    const start1 = timeStringToMinutes(time1.start);
    const end1 = timeStringToMinutes(time1.end);
    const start2 = timeStringToMinutes(time2.start);
    const end2 = timeStringToMinutes(time2.end);

    if ([start1, end1, start2, end2].some((v) => v === null)) return false;

    return start1 < end2 && end1 > start2;
};


export const lessonsHaveConflict = (lessonA, lessonB) => {
    const timesA = lessonA?.times || [];
    const timesB = lessonB?.times || [];
    for (const t1 of timesA) {
        for (const t2 of timesB) {
            if (timesOverlap(t1, t2)) return true;
        }
    }
    return false;
};
