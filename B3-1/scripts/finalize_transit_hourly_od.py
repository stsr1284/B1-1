"""Summarize completed raw acquisition; no passenger-count transformation."""
import csv
import json
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
META=ROOT/'data/metadata/transit_hourly_od'

def main():
    state=json.loads((META/'acquisition.json').read_text())
    if state['status']!='complete':raise SystemExit('Acquisition has not completed')
    records=[json.loads((ROOT/f['record']).read_text()) for f in state['files']]
    master=json.loads((META/'admin_master.json').read_text())
    with (ROOT/master['path']).open(encoding=master['encoding']) as f:
        master_rows=list(csv.DictReader(f))
    ids={r['행정동_ID'] for r in master_rows}
    years={};date_counts=defaultdict(int);coverage=[];unmatched={}
    for rec in records:
        y=rec['stamp'][:4];r=years.setdefault(y,{'files':0,'bytes':0,'rows':0,'observed_dates':set(),'missing_dates':[],'null_od_identifier_cells':0,'header_anomalies':0,'unmatched_area_ids':set()})
        r['files']+=1;r['bytes']+=rec['bytes'];r['rows']+=rec['rows'];r['observed_dates'].update(rec['observed_dates']);r['missing_dates']+=rec['missing_dates'];r['unmatched_area_ids'].update(set(rec['area_ids'])-ids)
        for member in rec['members']:
            r['null_od_identifier_cells']+=member.get('null_od_identifier_cells',0);r['header_anomalies']+=bool(member.get('raw_header_anomaly'))
            for date in member['dates']:date_counts[date]+=1
            coverage.append({'zip':rec['filename'],'member':member['name'],'rows':member['rows'],'dates':'|'.join(member['dates']),'header_only':member['header_only'],'null_od_identifier_cells':member.get('null_od_identifier_cells',0),'header_anomaly':bool(member.get('raw_header_anomaly'))})
    for y,r in years.items():
        r['observed_days']=len(r.pop('observed_dates'));r['missing_dates']=sorted(r['missing_dates']);r['unmatched_area_ids']=sorted(r['unmatched_area_ids'])
    duplicates={date:n for date,n in date_counts.items() if n>1}
    report={'status':'acquired_with_source_quality_caveats','source_url':records[0]['source_url'],'mode_scope':'bus and subway combined','time_basis':'source-reported hour; boarding/alighting attribution unconfirmed','years':years,'duplicate_dates_across_members':duplicates,'master_rows':len(master_rows),'master_distinct_ids':len(ids),'master_scope':'current snapshot only; historical administrative boundary and code stability not established','raw_content_modified':False,'numeric_cells_and_duplicate_od_keys':'not yet fully audited','checked_at':datetime.now(timezone.utc).isoformat()}
    old_path=ROOT/'tmp/2026-10-26/previous-results/data/spatial/hourly/sources.json'
    if old_path.exists():
        old={r['period'].replace('-',''):r for r in json.loads(old_path.read_text())['sources']}
        report['previous_2025_original_hash_comparison']=[{'stamp':r['stamp'],'same_sha256':r['sha256']==old[r['stamp']]['sha256']} for r in records if r['stamp'] in old]
    (META/'quality_summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    with (META/'daily_coverage.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(coverage[0]),lineterminator='\n');w.writeheader();w.writerows(coverage)
    catpath=ROOT/'data/metadata/catalog.json';cat=json.loads(catpath.read_text());files={r['path']:r for r in cat['files']}
    for r in records+[master]:
        p=ROOT/r['path'];assert p.stat().st_size==r['bytes']
        files[r['path']]={k:r[k] for k in ['path','bytes','sha256','source_url']}
        files[r['path']].update(role='raw',provenance_record=str((META/(r['stamp']+'.json' if 'stamp' in r else 'admin_master.json')).relative_to(ROOT)))
    cat['files']=sorted(files.values(),key=lambda r:r['path']);cat['total_raw_bytes']=sum(r['bytes'] for r in cat['files']);groups={}
    for r in cat['files']:
        parts=Path(r['path']).parts[2:];key='/'.join(parts[:2]) if parts[0]!='calendar' else 'calendar';g=groups.setdefault(key,{'files':0,'bytes':0});g['files']+=1;g['bytes']+=r['bytes']
    cat['groups']=groups;cat['inventory_updated_at']=report['checked_at'];cat.setdefault('integrity', {})['transit_hourly_od']={'files':len(records),'full_zip_crc':True,'every_record_date_checked':True,'schema':'27 columns; recorded header spelling repair only in memory','passenger_numeric_and_duplicate_keys':'not yet fully audited'}
    catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n')
    lines=['# 대중교통 시간대별 OD 원본 확보','', '**날짜·출발 행정동·도착 행정동·시간대별 이동 변화 분석에 사용할 원본이다. 버스와 지하철 합산이며 개별 수단을 분리할 수 없다.**','', '| 연도 | ZIP | 실제 데이터 날짜 | 원본 행 | 저장 용량 | 데이터 없는 날짜 |','|---|---:|---:|---:|---:|---:|']
    for y,r in sorted(years.items()):lines.append(f"| {y} | {r['files']} | {r['observed_days']:,}일 | {r['rows']:,} | {r['bytes']/1e9:.3f}GB | {len(r['missing_dates'])}일 |")
    lines+=['',f"확보 범위: **2023-01-01~2026-10-21**. 총 ZIP **{len(records)}개**, **{sum(r['bytes'] for r in records)/1e9:.3f}GB**. 2026년 1~9월은 월별 ZIP, 10월 1~21일은 일별 ZIP이다. 월별 ZIP 안에 날짜별 CSV가 있으므로 월 합계 자료와 다르다.",'','## 출처·열','', '[서울시 행정동 단위 대중교통 출발지/도착지 승객수 정보 OA-21226](https://data.seoul.go.kr/dataList/OA-21226/F/1/datasetView.do). 공식 다운로드 파일을 그대로 저장했고 API 키를 사용하지 않았다.','', '`기준_날짜`, `시작_행정동_ID`, `종료_행정동_ID`, `승객_수_00`~`승객_수_23`의 **27열**이다. 모두 기본 분석에 필요하다.','', '[행정동 마스터 OA-21234](https://data.seoul.go.kr/dataList/OA-21234/S/1/datasetView.do) 원본 2,270행도 확보했다. 7자리와 8자리 ID를 임의 변환하지 않고 문자열 그대로 연결한다. 현재 시점 마스터이며 과거 행정동 경계·명칭을 보장하지 않는다.','', '## 해석·사용 기준','', '- 시간 기준 미확정을 이유로 탐색 자체를 막지 않는다. **“18시 시간대로 집계된 성수 지역행 이동량”**처럼 표현하며 “18시 도착 인원”이라고 단정하지 않는다.','- 2023~2025 장기 추세와 전년 동기간·요일·시간대 비교에 사용한다. 2026년은 이전 연도의 같은 기간으로 비교하며 최신 부분 월은 별도로 표시한다.','- 같은 관측 날짜·시간대·공통 지역 코드 범위를 맞춘다. 누락 날짜와 빈 시간대 셀을 0으로 채우지 않는다. 시간대만으로 관광객 수·이동 목적을 확정하지 않는다.','- 지역별 유입·유출은 관측된 OD의 도착·출발 지역 기준이다. 같은 동 안 이동은 별도 분리하고 승하차 집계와 더하지 않는다.','- 27개 열 이름·배열은 비교 가능하지만 연도별 수집·집계 방식이 완전히 동일하다는 뜻은 아니다. 역사적 코드 변경과 결측 패턴을 분석 단계에서 확인한다.','', '## 실제 검증과 남은 검사','', '- 모든 ZIP CSV를 끝까지 읽어 CRC를 확인하고 SHA-256, 모든 행의 날짜, 열 배열, 빈 파일, 행정동 ID 결측을 기록했다. 압축 해제 사본을 디스크에 생성하지 않았다.','- 2023-06 일부 CSV 첫 열 이름에 불필요한 `?"`가 있다. 이를 기록하고 읽을 때만 해당 열을 `기준_날짜`로 대응했다. 원본 바이트는 수정하지 않았다.','- 출발/도착 ID가 빈 행은 원본에 보존했다. 지역명에 연결되지 않는 ID도 제외·추정하지 않고 아래 검증 기록에 남겼다.','- 확보 단계에서는 숫자 셀·OD 중복·지역 관측 여부를 전수 검사하지 않았다. 후속 분석 결과는 [최종 리포트](../REPORT.md)와 [완료 체크리스트](../docs/COMPLETION_CHECKLIST.md)를 따른다. 역사적 경계 불변은 확정하지 않았다.','', f'- 여러 원본 CSV에 중복으로 등장한 관측 날짜: {len(duplicates)}개.','', '## 경로·재현','', '```text','data/raw/transit_hourly_od/2023..2026/      공식 ZIP 원본','data/raw/locations/admin/transit_admin_master_20261027.csv','data/metadata/transit_hourly_od/            출처·해시·날짜별 검증','data/processed/                            향후 분석용 가공본','```','', '[파일별 상태](metadata/transit_hourly_od/acquisition.json) · [연도별 품질·누락일·미연결 ID](metadata/transit_hourly_od/quality_summary.json) · [날짜별 검증 CSV](metadata/transit_hourly_od/daily_coverage.csv)','', '수집: `scripts/acquire_transit_hourly_od.py`. 요약: `scripts/finalize_transit_hourly_od.py`. 검증 완료 파일은 SHA 대조 후 재사용하고 같은 수집 스크립트의 중복 실행은 잠금으로 막는다.','']
    (ROOT/'data/TRANSIT_OD.md').write_text('\n'.join(lines))
    print(json.dumps(years,ensure_ascii=False,indent=2));print('TOTAL',state['bytes'],state['observed_days'])

if __name__=='__main__':main()
