import random
import sqlite3

from faker import Faker
from faker.providers import BaseProvider


class OptimizedChineseAddressProvider(BaseProvider):
    def __init__(self, generator, db_path="my_data.db", table_name="cnarea_2016"):
        super().__init__(generator)
        self.db_path = db_path
        self.table_name = table_name
        self.conn = None  # Will be initialized in _get_connection
        self._get_connection()  # Establish connection

        # Cache provinces as they are few and frequently accessed
        self.provinces_data = self._load_specific_level_data("0")

        # For counting rows for efficient random selection
        self._counts = {}

    def _get_connection(self):
        if self.conn is None or self._is_connection_closed():
            try:
                self.conn = sqlite3.connect(self.db_path)
                self.conn.row_factory = sqlite3.Row  # Access columns by name
            except sqlite3.Error as e:
                print(f"Error connecting to database: {e}")
                self.conn = None  # Ensure conn is None if connection failed
                raise  # Re-raise the exception to signal failure
        return self.conn

    def _is_connection_closed(self):
        """Checks if the connection is closed or unusable."""
        if self.conn is None:
            return True
        try:
            # Try a simple no-op query to check connection status
            self.conn.execute("SELECT 1").fetchone()
            return False
        except (
            sqlite3.ProgrammingError
        ):  # Connection closed or cursor used on closed connection
            return True
        except sqlite3.Error:  # Other SQLite errors might indicate a problem
            return True

    def __del__(self):
        """Ensure the database connection is closed when the provider is garbage collected."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def _execute_query(self, query, params=None, fetch_one=False):
        """Helper to execute queries and handle connection."""
        conn = self._get_connection()
        if not conn:
            return None if fetch_one else []

        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            if fetch_one:
                row = cursor.fetchone()
                return dict(row) if row else None  # <--- MODIFIED HERE
            else:
                rows = cursor.fetchall()
                return [dict(row) for row in rows]  # <--- MODIFIED HERE
        except sqlite3.Error as e:
            print(f"SQLite error: {e} for query: {query} with params: {params}")
            return None if fetch_one else []

    def _load_specific_level_data(self, level):
        """Loads all data for a specific level (e.g., '0' for provinces)."""
        query = f"SELECT level, area_code, zip_code, city_code, name, short_name FROM {self.table_name} WHERE level = ?"
        return self._execute_query(query, (level,))

    def _get_random_row_from_db(
        self, conditions_sql="", params=None, level_for_count=None
    ):
        conn = self._get_connection()
        if not conn:
            return None

        # Use a more robust cache key including params and level_for_count
        param_tuple = tuple(params) if params is not None else tuple()
        count_key = (conditions_sql, param_tuple, level_for_count)

        if level_for_count and count_key in self._counts:
            count = self._counts[count_key]
        else:
            # Use an alias for COUNT(*) for robust dictionary key access
            count_query = f"SELECT COUNT(*) as total_count FROM {self.table_name} WHERE {conditions_sql if conditions_sql else '1=1'}"

            # _execute_query now returns a dict like {'total_count': N} or None
            count_result_dict = self._execute_query(count_query, params, fetch_one=True)

            if count_result_dict and "total_count" in count_result_dict:
                count = count_result_dict["total_count"]
            else:
                count = 0  # Default to 0 if count couldn't be retrieved

            # Ensure count is a non-negative integer
            if not isinstance(count, int) or count < 0:
                count = 0

            if level_for_count:  # Cache the count (even if 0)
                self._counts[count_key] = count

        if count == 0:
            return None

        random_offset = random.randint(0, count - 1)
        query = f"SELECT level, area_code, zip_code, city_code, name, short_name FROM {self.table_name} WHERE {conditions_sql if conditions_sql else '1=1'} LIMIT 1 OFFSET ?"

        final_params = list(params or [])
        final_params.append(random_offset)

        return self._execute_query(query, tuple(final_params), fetch_one=True)

    def province_detail(self):
        """Returns a dictionary with province details from cached data."""
        return random.choice(self.provinces_data) if self.provinces_data else None

    def province_name(self, use_short_name=False):
        province = self.province_detail()
        if not province:
            return "N/A"
        return (
            province["short_name"]
            if use_short_name and province.get("short_name")
            else province["name"]
        )

    def city_detail(self, province_area_code=None):
        """Returns a dictionary with city details by querying the DB."""
        conditions = "level = '1'"
        params = []
        if province_area_code:
            prefix = province_area_code[:2]  # e.g., '44' from '440000'
            # Cities under a province: XXYY00 where XX is province prefix, YY is not 00.
            conditions += f" AND SUBSTR(area_code, 1, 2) = ? AND SUBSTR(area_code, 3, 2) != '00' AND SUBSTR(area_code, 5, 2) = '00'"
            params.append(prefix)

        # Use '1' (level for cities) as part of the key for count caching
        return self._get_random_row_from_db(
            conditions, tuple(params), level_for_count="1"
        )

    def city_name(self, province_area_code=None, use_short_name=False):
        city = self.city_detail(province_area_code)
        if not city:
            return "N/A"
        return (
            city["short_name"]
            if use_short_name and city.get("short_name")
            else city["name"]
        )

    def district_detail(self, city_area_code=None):
        """Returns a dictionary with district details by querying the DB."""
        conditions = "level = '2'"
        params = []
        if city_area_code:
            prefix = city_area_code[:4]  # e.g., '4401' from '440100'
            # Districts under a city: XXYYZZ where XXYY is city prefix, ZZ is not 00.
            conditions += (
                f" AND SUBSTR(area_code, 1, 4) = ? AND SUBSTR(area_code, 5, 2) != '00'"
            )
            params.append(prefix)

        # Use '2' (level for districts) as part of the key for count caching
        return self._get_random_row_from_db(
            conditions, tuple(params), level_for_count="2"
        )

    def district_name(self, city_area_code=None, use_short_name=False):
        district = self.district_detail(city_area_code)
        if not district:
            return "N/A"
        return (
            district["short_name"]
            if use_short_name and district.get("short_name")
            else district["name"]
        )

    def zipcode(self, district_area_code=None):
        """Returns a zip code by querying the DB if necessary."""
        district_data = None
        if district_area_code:
            query = f"SELECT zip_code FROM {self.table_name} WHERE area_code = ? AND level = '2' LIMIT 1"
            row = self._execute_query(query, (district_area_code,), fetch_one=True)
            if row:
                return row["zip_code"]
        else:
            # Get a random district detail (which queries DB)
            district_data = self.district_detail()
            if district_data and district_data.get("zip_code"):
                return district_data["zip_code"]
        return "000000"  # Default or fallback

    def full_chinese_address_detail(self, use_short_names=True):
        prov = self.province_detail()  # From cache
        if not prov:
            return {"address": "省份数据加载失败", "zip_code": "N/A"}

        prov_name_part = (
            prov["short_name"]
            if use_short_names and prov.get("short_name")
            else prov["name"]
        )
        prov_code = prov["area_code"]

        city = self.city_detail(province_area_code=prov_code)  # DB Query
        city_name_part = ""
        city_code = None
        dist_name_part = ""
        zip_code_part = prov.get(
            "zip_code", "000000"
        )  # Default to province zip if others fail

        if city:
            city_name_part = (
                city["short_name"]
                if use_short_names and city.get("short_name")
                else city["name"]
            )
            city_code = city["area_code"]
            zip_code_part = (
                city.get("zip_code") or zip_code_part
            )  # City zip or fallback to province zip

            dist = self.district_detail(city_area_code=city_code)  # DB Query
            if dist:
                dist_name_part = (
                    dist["short_name"]
                    if use_short_names and dist.get("short_name")
                    else dist["name"]
                )
                zip_code_part = (
                    dist.get("zip_code") or zip_code_part
                )  # District zip or fallback to city/province zip

        # Faker's street address part
        street = f"{self.generator.street_name()}{random.randint(1, 300)}号"

        address_parts = []
        if (
            prov_name_part == city_name_part and city_name_part
        ):  # Municipalities like Beijing
            address_parts = [prov_name_part, dist_name_part, street]
        else:
            address_parts = [prov_name_part, city_name_part, dist_name_part, street]

        full_address = "".join(part for part in address_parts if part)

        return {
            "province": prov_name_part,
            "city": city_name_part if city_name_part else "N/A",
            "district": dist_name_part if dist_name_part else "N/A",
            "street_address": street,
            "full_address": full_address,
            "zip_code": zip_code_part if zip_code_part else "000000",
            "area_codes": {
                "province": prov_code,
                "city": city_code if city_code else "N/A",
                "district": dist["area_code"] if "dist" in locals() and dist else "N/A",
            },
        }


# --- (create_sample_cnarea_db function remains the same as before) ---
# ... (from previous answer)
def create_sample_cnarea_db(db_path="my_data.db", table_name="cnarea_2016"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    cursor.execute(
        f"""
    CREATE TABLE {table_name} (
        uid INTEGER PRIMARY KEY AUTOINCREMENT,
        level VARCHAR(64),
        area_code VARCHAR(64) UNIQUE,
        zip_code VARCHAR(64),
        city_code VARCHAR(64),
        area_name VARCHAR(64),
        name VARCHAR(64),
        short_name VARCHAR(64),
        lng VARCHAR(64),
        lat VARCHAR(64)
    )
    """
    )
    # Add Indexes - CRITICAL FOR PERFORMANCE
    cursor.execute(
        f"CREATE INDEX IF NOT EXISTS idx_{table_name}_level ON {table_name}(level);"
    )
    cursor.execute(
        f"CREATE INDEX IF NOT EXISTS idx_{table_name}_area_code ON {table_name}(area_code);"
    )
    # Index for SUBSTR optimizations if your SQLite version supports indexed expressions,
    # otherwise the SUBSTR operations will scan the level index or area_code index.
    # cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_areacode_prefix2 ON {table_name}(SUBSTR(area_code, 1, 2));")
    # cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_areacode_prefix4 ON {table_name}(SUBSTR(area_code, 1, 4));")
    # The above substring indexes are more advanced. Start with level and area_code.

    sample_data = [
        ("0", "110000", "100000", "010", "北京市", "北京市", "北京"),
        ("1", "110100", "100000", "010", "北京市市辖区", "市辖区", "市辖区"),
        ("2", "110101", "100010", "010", "北京市东城区", "东城区", "东城"),
        ("0", "440000", "510000", "020", "广东省", "广东省", "广东"),
        ("1", "440100", "510000", "020", "广东省广州市", "广州市", "广州"),
        ("2", "440103", "510030", "020", "广东省广州市荔湾区", "荔湾区", "荔湾"),
        ("2", "440106", "510630", "020", "广东省广州市天河区", "天河区", "天河"),
        ("1", "440300", "518000", "0755", "广东省深圳市", "深圳市", "深圳"),
        ("2", "440301", "518028", "0755", "广东省深圳市福田区", "福田区", "福田"),
    ]
    cursor.executemany(
        f"INSERT INTO {table_name} (level, area_code, zip_code, city_code, name, short_name) VALUES (?, ?, ?, ?, ?, ?)",
        [(d[0], d[1], d[2], d[3], d[5], d[6]) for d in sample_data],
    )
    conn.commit()
    conn.close()
    print(f"Sample database '{db_path}' created with table '{table_name}' and indexes.")


# --- 主程序，添加并使用 Provider ---
if __name__ == "__main__":
    DB_FILE = "my_cn_data_optimized.db"
    TABLE_NAME = "cnarea_2016"
    create_sample_cnarea_db(
        db_path=DB_FILE, table_name=TABLE_NAME
    )  # Create sample DB with indexes

    fake = Faker("zh_CN")

    # Using the optimized provider
    address_provider_opt = OptimizedChineseAddressProvider(
        fake, db_path=DB_FILE, table_name=TABLE_NAME
    )
    fake.add_provider(address_provider_opt)

    print("\n--- Optimized Address Info ---")

    print("\nRandom Province (from cache):")
    for _ in range(2):
        prov_detail = (
            fake.province_detail()
        )  # method from OptimizedChineseAddressProvider
        if prov_detail:
            print(
                f"  Name: {prov_detail['name']}, Area Code: {prov_detail['area_code']}"
            )

    print("\nRandom City (DB query):")
    for _ in range(2):
        city_detail = fake.city_detail()
        if city_detail:
            print(
                f"  Name: {city_detail['name']}, Area Code: {city_detail['area_code']}"
            )

    print("\nRandom District from Guangzhou (city_area_code='440100', DB query):")
    guangzhou_code = "440100"
    for _ in range(2):
        dist_detail = fake.district_detail(city_area_code=guangzhou_code)
        if dist_detail:
            print(
                f"  Name: {dist_detail['name']}, Area Code: {dist_detail['area_code']}, Zip: {dist_detail['zip_code']}"
            )
        else:
            print(f"  No district found for Guangzhou (or DB error).")

    print("\nFull Address Detail (multiple DB queries per call):")
    for i in range(3):
        print(f"\nAddress {i+1}:")
        details = fake.full_chinese_address_detail(use_short_names=True)
        for key, value in details.items():
            if isinstance(value, dict):  # For area_codes
                print(f"  {key.capitalize()}:")
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key.capitalize()}: {sub_value}")
            else:
                print(f"  {key.capitalize()}: {value}")

    # Clean up: The __del__ method in the provider will attempt to close the connection
    # when address_provider_opt goes out of scope or is deleted.
    # For explicit cleanup:
    # del address_provider_opt
    # del fake
