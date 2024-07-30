from datetime import datetime, date
from pytz import timezone

source = "20241126T144500Z"
print("source = ", source)

def convert_timestamp(input: str) -> datetime:
    """Permet de convertir les timestamp en ISO-8601, et les passer en UTC+2"""
    iso_date = f"{input[0:4]}-{input[4:6]}-{input[6:11]}:{input[11:13]}:{input[13:]}"
    return datetime.fromisoformat(iso_date).astimezone(timezone("Europe/Paris"))


source_convert = datetime.now().replace(microsecond=0)
print("source_convert = ", source_convert)
source_convert_time = source_convert.astimezone(timezone("UTC"))
print("source_convert_time = ", source_convert_time)
source_convert_time_iso = source_convert_time.isoformat()
print("source_convert_time_iso = ", source_convert_time_iso)
source_convert_time_iso_parce = str(source_convert_time_iso).replace("-", "").replace(":", "").replace("+0000","Z")
print("source_convert_time_iso_parce = ", source_convert_time_iso_parce)

final = str(source_convert.astimezone(timezone("UTC")).isoformat()).replace("-", "").replace(":", "").replace("+0000","Z")

print("final = ",final)


