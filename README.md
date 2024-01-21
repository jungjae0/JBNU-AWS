## 전북대학교 학습도서관 AWS 기상대 시각화 및 데이터 다운로드

**link > https://jbnu-aws.streamlit.app/**

<details>
<summary>Streamlit APP</summary>
데이터 기간: 2023.10.01 ~ 전날

Daily: 'select a(an) start/end date' 에서 선택한 기간
Day: 'select a date' 에서 선택한 날짜

| Tab           | Data  | Contents                                                                             |
|---------------|-------|--------------------------------------------------------------------------------------|
| Day Vis       | Day   | - 온습도<br/>- 온도<br/>- 습도<br/>- 누적광량                                                   |
| Daily Vis     | Daily | - 온습도<br/>- 온도<br/>- 습도<br/>- 누적광량<br/>- 일교차<br/>- 온도&강수량<br/>- 강수계급별 분포<br/>- 풍향 분포 |
| Summary Table | Daily | - 요약 통계 데이터                                                                          |
| Hour Table    | Daily | - 1시간 간격 전체 데이터                                                                      |
| Minute Table  | Daily | - 설정 분 간격 전체 데이터                                                                     |
| Day Table     | Day   | - 설정 분 간격 전체 데이터                                                                     |
</details>


<details>
<summary>AWS 데이터 명세서</summary>

| 구분                | name     | 단위                  |
|-------------------|----------|---------------------|
| datetime          | datetime | YYYY-MM-DD hh:mm:ss |
| 온도                | temp     | ℃                   |
| 습도                | hum      | %                   |
| 일사                | rad      | W/m^2               |
| 풍향                | wd       | degree              |
| 풍속                | ws       | m/s                  |
| 강우                | rain     | mm                  |
| 최대순간풍속(60초 중 최고값) | maxws    | m/s                 |
| 배터리전압(최저값)        | bv       | V                   |
</details>

<details>
<summary>AWS Summary 데이터 명세서</summary>

| 구분   | 단위    | 설명                                            |
|------|-------|-----------------------------------------------|
| 평균기온 | ℃     | 일 평균 기온                                       |
| 최고기온 | ℃     | 일 최고 기온                                       |
| 최저기온 | ℃     | 일 최저 기온                                       |
| 강수량  | mm    | 일 총 강수량                                       |
| 최대일사 | W/m^2 | 일 최대 일사량                                      |
| 일교차  | ℃     | 일 최고 기온 - 일 최고 기온                             |
| 강수계급 | -     | 강수량에 따라 5개 단계로 구분                             |
| 풍향계급 | -     | 풍향에 따라 16개 방향으로 구분                            |
| 적산온도 | ℃     | 생육일수의 일평균기온을 적산                               |
| 강수일수 | 일     | -                                             |
| 폭염일수 | 일     | -                                             |
| 한파일수 | 일     | -                                             |
| 체감온도 | ℃     | 인간이 느끼는 더위나 추위를 수량적으로 나타낸 것                   |
| 실효습도 | %     | 수일 전부터의 상대습도에 경과 시간에 따른 가중치를 주어서 건조도를 나타내는 지수 |

※ 해당 데이터에서는 실효습도, 적산온도 무의미함

</details>



### 데이터 수동 저장

```aws2csv.py``` > 시작/끝 날짜 설정 후 실행

```python
start_date_str = "20231101" # 시작 날짜
end_date_str = "20231106"   # 끝 날짜
```