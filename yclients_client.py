# yclients_client.py
import requests
from typing import Any, Dict, Optional

BASE = "https://api.yclients.com/api/v1"
ACCEPT = "application/vnd.yclients.v2+json"

class YClientsError(RuntimeError):
    def __init__(self, status: int, meta: Any):
        super().__init__(f"YClients API error (HTTP {status}): {meta}")
        self.status = status
        self.meta = meta

class YClientsClient:
    def __init__(self, partner_token: str, user_token: str, timeout: int = 30):
        self.partner_token = partner_token
        self.user_token = user_token
        self.timeout = timeout
        self.session = requests.Session()
        # Все вызовы используют объединённый заголовок:
        self.session.headers.update({
            "Accept": ACCEPT,
            "Authorization": f"Bearer {self.partner_token}, User {self.user_token}",
            # Никакого Partner-Token отдельно — он уже в Authorization
        })

    # --- низкоуровневые вызовы ---
    def _handle(self, r: requests.Response) -> Dict[str, Any]:
        status = r.status_code
        
        # Для status 204 (No Content) zwracamy sukces bez parsowania JSON
        if status == 204:
            return {"success": True, "data": None, "meta": []}
        
        try:
            data = r.json()
        except Exception:
            r.raise_for_status()  # поднимет HTTPError с телом, если не JSON
        if status >= 400 or not data.get("success", False):
            raise YClientsError(status, data.get("meta"))
        return data

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        import logging
        log = logging.getLogger()
        log.info(f"🌐 YCLIENTS GET REQUEST: {BASE}{path}")
        log.info(f"🌐 YCLIENTS PARAMS: {params}")
        log.info(f"🌐 YCLIENTS HEADERS: {dict(self.session.headers)}")
        
        r = self.session.get(f"{BASE}{path}", params=params, timeout=self.timeout)
        log.info(f"🌐 YCLIENTS RESPONSE STATUS: {r.status_code}")
        log.info(f"🌐 YCLIENTS RESPONSE HEADERS: {dict(r.headers)}")
        log.info(f"🌐 YCLIENTS RESPONSE BODY: {r.text[:500]}...")
        
        return self._handle(r)

    def post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        import logging
        log = logging.getLogger()
        log.info(f"🌐 YCLIENTS POST REQUEST: {BASE}{path}")
        log.info(f"🌐 YCLIENTS PAYLOAD: {payload}")
        log.info(f"🌐 YCLIENTS HEADERS: {dict(self.session.headers)}")
        
        r = self.session.post(f"{BASE}{path}", json=payload, timeout=self.timeout)
        log.info(f"🌐 YCLIENTS RESPONSE STATUS: {r.status_code}")
        log.info(f"🌐 YCLIENTS RESPONSE HEADERS: {dict(r.headers)}")
        log.info(f"🌐 YCLIENTS RESPONSE BODY: {r.text[:500]}...")
        
        return self._handle(r)

    def put(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        r = self.session.put(f"{BASE}{path}", json=payload, timeout=self.timeout)
        return self._handle(r)

    # --- удобные методы ---
    def my_companies(self) -> Dict[str, Any]:
        return self.get("/companies/", params={"my": 1})

    def company_services(self, company_id: int) -> Dict[str, Any]:
        # список услуг
        return self.get(f"/services/{company_id}")

    def company_masters(self, company_id: int) -> Dict[str, Any]:
        # список мастеров
        return self.get(f"/staff/{company_id}")

    def company_records(self, company_id: int) -> Dict[str, Any]:
        # список записей компании
        return self.get(f"/records/{company_id}")

    def find_client_by_phone(self, company_id: int, phone: str) -> Dict[str, Any]:
        # поиск клиента по телефону (форматируй телефон так, как хранится в YClients)
        return self.get(f"/clients/{company_id}", params={"search": phone})

    def create_client(self, company_id: int, *, name: str, phone: str,
                      email: str = "", comment: str = "") -> Dict[str, Any]:
        payload = {
            "name": name,
            "phone": phone,
            "email": email,
            "comment": comment
        }
        return self.post(f"/clients/{company_id}", payload)

    def create_record(self, company_id: int, *,
                      service_id: int, staff_id: int,
                      date_time: str,  # "YYYY-MM-DD HH:MM"
                      client_id: Optional[int] = None,
                      client: Optional[Dict[str, Any]] = None,
                      comment: str = "", seance_length: Optional[int] = None) -> Dict[str, Any]:
        """
        date_time — локальное время филиала, формат 'YYYY-MM-DD HH:MM'
        либо проверь в документации/ответе компании её timezone_name и приводи время.
        """
        payload = {
            "staff_id": staff_id,
            "services": [{"id": service_id}],
            "datetime": date_time,
            "comment": comment
        }
        
        # Добавляем длительность сеанса если указана
        if seance_length:
            payload["seance_length"] = seance_length
        
        if client_id:
            # Если есть client_id, создаем объект client
            payload["client"] = {"id": client_id}
        elif client:
            # пример client: {"name":"Иван", "phone":"+7999...", "email":"..."}
            payload["client"] = client
        else:
            raise ValueError("Either client_id or client object must be provided")
            
        return self.post(f"/records/{company_id}", payload)

    def delete_record(self, company_id: int, record_id: int) -> Dict[str, Any]:
        """Удалить запись"""
        import logging
        log = logging.getLogger()
        log.info(f"🗑️ YCLIENTS DELETE REQUEST: {BASE}/record/{company_id}/{record_id}")
        
        r = self.session.delete(f"{BASE}/record/{company_id}/{record_id}", timeout=self.timeout)
        log.info(f"🗑️ YCLIENTS DELETE RESPONSE STATUS: {r.status_code}")
        log.info(f"🗑️ YCLIENTS DELETE RESPONSE BODY: {r.text[:500]}...")
        
        return self._handle(r)

    def update_record(self, company_id: int, record_id: int, **kwargs) -> Dict[str, Any]:
        """Изменить запись"""
        import logging
        log = logging.getLogger()
        log.info(f"✏️ YCLIENTS PUT REQUEST: {BASE}/record/{company_id}/{record_id}")
        log.info(f"✏️ YCLIENTS PUT PAYLOAD: {kwargs}")
        
        r = self.session.put(f"{BASE}/record/{company_id}/{record_id}", json=kwargs, timeout=self.timeout)
        log.info(f"✏️ YCLIENTS PUT RESPONSE STATUS: {r.status_code}")
        log.info(f"✏️ YCLIENTS PUT RESPONSE BODY: {r.text[:500]}...")
        
        return self._handle(r)

    # --- методы для работы с записями пользователей ---
    def get_user_record(self, record_id: int, record_hash: str) -> Dict[str, Any]:
        """Получить запись пользователя по ID и хешу"""
        return self.get(f"/user/records/{record_id}/{record_hash}")

    def delete_user_record(self, record_id: int, record_hash: str) -> Dict[str, Any]:
        """Удалить запись пользователя"""
        return self.session.delete(f"{BASE}/user/records/{record_id}/{record_hash}", timeout=self.timeout)

    def send_phone_code(self, company_id: int, phone: str, fullname: str = "") -> Dict[str, Any]:
        """Отправить SMS код подтверждения номера телефона"""
        payload = {"phone": phone}
        if fullname:
            payload["fulname"] = fullname
        return self.post(f"/book_code/{company_id}", payload)

    def auth_by_phone_code(self, phone: str, code: str) -> Dict[str, Any]:
        """Авторизоваться по номеру телефона и коду"""
        payload = {"phone": phone, "code": code}
        return self.post("/user/auth", payload)

# ==== пример использования ====
if __name__ == "__main__":
    PARTNER_TOKEN = "nudftdeweddp2n6g7hhw"  # твой реальный партнёрский
    USER_TOKEN    = "652f770cc7224fda91f886b1efa7fe01"  # получен через /auth

    api = YClientsClient(PARTNER_TOKEN, USER_TOKEN)

    # 1) Мои компании
    companies = api.my_companies()
    print("My companies:", companies["data"])

    # Возьмём первую компанию
    company_id = companies["data"][0]["id"]

    # 2) Мастера и услуги
    masters  = api.company_masters(company_id)
    services = api.company_services(company_id)
    print("Masters count:", len(masters.get("data", [])))
    print("Services count:", len(services.get("data", [])))

    # 3) Поиск клиента по телефону
    found = api.find_client_by_phone(company_id, "79939554531")
    print("Found clients:", found.get("data", []))

    # 4) Создать запись (пример — проверь реальные service_id/staff_id и корректное локальное время!)
    # api.create_record(
    #     company_id,
    #     service_id=<SERVICE_ID>,
    #     staff_id=<MASTER_ID>,
    #     date_time="2025-10-28 12:30",
    #     client_id=found["data"][0]["id"] if found.get("data") else None,
    #     client=None if found.get("data") else {"name":"Надежда","phone":"79939554531"},
    #     comment="Онлайн запись с сайта"
    # )
