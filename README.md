## 重要之套件版本

`python` &ge 3.7

`gdal` &ge 3.0.0

`numpy` &ge 1.16.4-1

`numba` &ge 0.49.1
## 稜線檔案限制
稜線圖層之ridge必須設定其值為255, non-ridge 則不限定

## 執行方式
`pythom main.py -i 稜線檔名.tif -o 輸出tsi圖層檔名.tif`

## 設計理念
- 使用脊點編號法,預先歸納八方位脊點,以避免暴力搜索重複運算之次數。
- 善用Numba套件,大幅改善Python動態編譯造成之計算效率問題,於大型圖層計算中尤為重要
