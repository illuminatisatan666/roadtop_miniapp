let map;
let multiRoute;

// Инициализация
Telegram.WebApp.ready();

function initMap() {
    ymaps.ready(() => {
        map = new ymaps.Map("map", {
            center: [55.75, 37.61],
            zoom: 6
        });
    });
}

// Построение маршрута по адресам
async function buildRoute() {
    const from = document.getElementById("from-input").value.trim();
    const to = document.getElementById("to-input").value.trim();

    if (!from || !to) return alert("Введите 'откуда' и 'куда'");

    // Геокодирование
    const fromGeo = await ymaps.geocode(from);
    const toGeo = await ymaps.geocode(to);

    const fromPoint = fromGeo.geoObjects.get(0)?.geometry?.getCoordinates();
    const toPoint = toGeo.geoObjects.get(0)?.geometry?.getCoordinates();

    if (!fromPoint || !toPoint) return alert("Не удалось найти адрес");

    // Удаляем старый маршрут
    if (multiRoute) map.geoObjects.remove(multiRoute);

    // Строим маршрут
    multiRoute = new ymaps.multiRouter.MultiRoute({
        referencePoints: [fromPoint, toPoint],
        params: { routingMode: 'auto' }
    }, {
        boundsAutoApply: true
    });

    map.geoObjects.add(multiRoute);
    map.setCenter(fromPoint, 6);
}

// Загрузка топ-мест рядом с маршрутом
async function loadNearbyPlaces() {
    const res = await fetch("/api/places");
    const places = await res.json();
    const list = document.getElementById("places");
    list.innerHTML = "";

    places.forEach(p => {
        const dist = distance(
            multiRoute?.getRoutes?.()?.get(0)?.getPaths?.()?.get(0)?.getSegments?.()?.get(0)?.getCoordinates?.()[0],
            [p.lat, p.lon]
        );
        if (dist < 50) { // в пределах 50 км от маршрута
            const li = document.createElement("li");
            li.innerHTML = `<b>${p.name}</b> — ${p.review.substring(0, 60)}...`;
            list.appendChild(li);
        }
    });
}

// Упрощённый расчёт расстояния (в км)
function distance(p1, p2) {
    if (!p1) return 999;
    const R = 6371;
    const dLat = (p2[0] - p1[0]) * Math.PI / 180;
    const dLon = (p2[1] - p1[1]) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(p1[0] * Math.PI / 180) * Math.cos(p2[0] * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

// Инициализация
initMap();