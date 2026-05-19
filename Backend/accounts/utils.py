import pandas as pd
import re

def parse_instructors(instructor_responsibility_text):
    if not instructor_responsibility_text or pd.isna(instructor_responsibility_text):
        return []
    pattern = r'([^:\n]+?)\s*:\s*استاد\s+درس'
    matches = re.findall(pattern, str(instructor_responsibility_text))
    return [name.strip() for name in matches if name.strip()]


def parse_schedule_and_exam(time_text):
    times_list = []
    exam_info = {}
    
    if not time_text or pd.isna(time_text):
        return times_list, exam_info

    day_map = {
        'یکشنبه': 1, 
        'دوشنبه': 2, 
        'سهشنبه': 3, 
        'چهارشنبه': 4, 
        'پنجشنبه': 5, 
        'جمعه': 6,
        'شنبه': 0, 
    }

    # ۱. پاک‌سازی فاصله‌های اضافی و یکدست‌سازی متن
    text = " ".join(str(time_text).split())
    
    # ۲. پیدا کردن نقاط شروع هر بخش (درس تئوری، عملی، حل تمرین یا امتحان)
    # این رگکس تمام عبارات کلیدی را پیدا می‌کند تا متن را از آنجا برش بزنیم
    delimiters = r'(درس\(ت\):|درس\(ع\):|درس\(ح\):|حل تمرین:|امتحان\([^)]+\))'
    
    # تفکیک متن؛ تکه‌های جدا شده شامل خود کلمات کلیدی هم خواهند بود
    tokens = re.split(delimiters, text)
    
    # بخش‌های تفکیک شده را به صورت جفت (کلمه کلیدی + محتوای بعد از آن) در می‌آوریم
    parts = []
    current_header = ""
    
    for token in tokens:
        token = token.strip()
        if not token:
            continue
        # اگر توکن یکی از هدرها یا بخش امتحان باشد
        if re.match(r'^(درس\(.\):|حل تمرین:|امتحان\([^)]+\))$', token):
            current_header = token
        else:
            if current_header:
                parts.append(f"{current_header} {token}")
                current_header = ""
            else:
                # اگر متنی بدون هدر آمد (مثلا ابتدای رشته)
                parts.append(token)
                
    # اگر آخرین توکن یک هدر تنها بود (بدون متن بعدی، مثلا فقط مشخصات امتحان)
    if current_header and current_header.startswith('امتحان'):
        parts.append(current_header)

    # ۳. پردازش هر بخش به صورت مجزا
    for part in parts:
        part = part.strip()
        
        if 'امتحان' in part:
            # استخراج تاریخ امتحان از بین پرانتزها
            exam_date_match = re.search(r'امتحان\((.*?)\)', part)
            # استخراج ساعت امتحان (مثلا ۱۳:۳۰-۱۵:۳۰)
            exam_time_match = re.search(r'ساعت\s*:\s*([\d:]+)-([\d:]+)', part)
            
            if exam_date_match:
                raw_date = exam_date_match.group(1).strip()
                # تبدیل '3_1405.04.01' به '1405.04.01'
                if '_' in raw_date:
                    exam_info['date'] = raw_date.split('_')[1].strip()
                else:
                    exam_info['date'] = raw_date
            if exam_time_match:
                exam_info['start_time'] = exam_time_match.group(1).strip()
                exam_info['end_time'] = exam_time_match.group(2).strip()
                
        else:
            # بررسی نوع کلاس (عملی، تئوری یا حل تمرین)
            is_exercise = 'حل تمرین' in part or '(ح)' in part

            clean_part_for_day = part.replace(" ", "").replace("\u200c", "").replace("\u200f", "")
            
            # استخراج روز هفته
            day_found = None
            for day_name, day_num in day_map.items():
                if day_name in clean_part_for_day:
                    day_found = day_num
                    #print(f"✅ Found in loop: {day_name} -> {day_num}")
                    break
            
            #print('day: ' + day_found)
            #print(f"Day name: {day_name}, Day num: {day_num}")
            #print(f"Clean part: {clean_part_for_day}")
            #print(f"Day found: {day_found}")
            
            # استخراج بازه زمانی (ساعت:دقیقه - ساعت:دقیقه)
            time_match = re.search(r'(\d{1,2}:\d{2})-(\d{1,2}:\d{2})', part)
            
            # استخراج آدرس مکان (گرفتن تمام کلمات بعد از "مکان:" تا زمانی که به هدر بعدی نرسیده‌ایم)
            # این رگکس اجازه می‌دهد مکان‌های چند کلمه‌ای مثل "كلاس 7 مركز زبان" به طور کامل استخراج شوند
            location_match = re.search(r'مکان\s*:\s*(.*?)(?:درس\(|امتحان\(|$)', part)
            location = location_match.group(1).strip() if location_match else "نامشخص"
            
            if day_found is not None and time_match:
                start_str = time_match.group(1)
                end_str = time_match.group(2)
                
                # استانداردسازی فرمت ساعت (تبدیل 8:00 به 08:00 برای هماهنگی با ولیدیشن مدل)
                if len(start_str.split(':')[0]) == 1: start_str = "0" + start_str
                if len(end_str.split(':')[0]) == 1: end_str = "0" + end_str
                
                times_list.append({
                    'day': day_found,
                    'start': start_str,
                    'end': end_str,
                    'isExerciseSolving': is_exercise,
                    'location': location
                })
                
    return times_list, exam_info


def normalize_fa_text(text):
    """
    تبدیل حروف عربی (ي و ك) به حروف استاندارد فارسی (ی و ک)
    """
    if not text or pd.isna(text):
        return ""
    
    text = str(text)
    text = text.replace('ي', 'ی')
    text = text.replace('ك', 'ک')
    
    return text.strip()