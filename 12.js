// ---- دالة عرض القراءات (معدلة للفلترة) ----
function displayReadings(readings) {
    readingsContainer.innerHTML = ''; // مسح المحتوى السابق

    if (!readings || readings.length === 0) {
        readingsContainer.innerHTML = '<div class="placeholder-text">لا توجد قراءات متاحة لهذا اليوم.</div>';
        return;
    }

    // 1. اختار الأقسام اللي عايز تعرضها هنا
    // شوف أسماء الأقسام اللي بتيجي من الـ API في الـ Console (F12)
    // غالباً هتكون زي: "البولس"، "الكاثوليكون"، "الإبركسيس"، "الإنجيل"، "المزمور"، "باكر"، إلخ
    const sectionsToShow = ["البولس", "الإنجيل"]; // مثال: عايز البولس والإنجيل بس

    // 2. فلتر القراءات
    const filteredReadings = readings.filter(reading => {
        const title = reading.title || reading.name || '';
        // لو العنوان فيه أي كلمة من اللي اختارناها، هنعرضه
        return sectionsToShow.some(section => title.includes(section));
    });

    if (filteredReadings.length === 0) {
        readingsContainer.innerHTML = '<div class="placeholder-text">لا توجد قراءات مطابقة للفلتر المحدد.</div>';
        return;
    }

    // 3. اعرض القراءات المفلترة
    filteredReadings.forEach(reading => {
        const card = document.createElement('div');
        card.className = 'reading-card';

        const title = document.createElement('h3');
        title.textContent = reading.title || reading.name || 'قراءة';
        card.appendChild(title);

        const text = document.createElement('p');
        text.textContent = reading.text || reading.content || reading.verses || 'لا يوجد نص.';
        card.appendChild(text);

        readingsContainer.appendChild(card);
    });
}