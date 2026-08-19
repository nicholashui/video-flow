# Video Flow
## 從創作意圖到可審計影片管道
### 技術書・第一部分：問題、演進、管治與控制平面

**版本基線：** Video Flow v3.0  
**文件性質：** 技術規格導讀與架構論述  
**語言：** 繁體中文（香港）

> **本書的立場**  
> Video Flow 是一份製作系統規格，而不是已部署、可即時使用的軟件產品。本書解釋規格所要求的行為、資料邊界與管治理由；除非明確標示為已定義的規範性要求，文字不應被理解為現有服務、介面、供應商整合或效能承諾。所有成本、模型能力、平台欄位與工作流程仍須在實作、試點、合約及部署環境中驗證。

---

## 讀者指南與範圍

本書面向要把生成式影片由「可做出一段片」提升為「可交代一段片如何被製作、核准、修復及發布」的製作負責人、系統架構師、工作流程工程師、創意技術人員與品質／合規人員。閱讀時請把 Video Flow 視作一條受管治的製作管道：模型可以提出影像、聲音或分析，但不能自行授權成本、覆蓋人員決定，或讓內容變成公開。

第一部分只建立全書的共同語言，涵蓋產品問題、三個版本的演進、設計原則，以及 v3 的最終架構和控制平面概觀。它不會展開後續各章的實作細節、完整資料契約、演算法、測試案例或部署指引。文中「**設計意圖**」說明規格要防止的失敗模式；「**開放問題**」則保留規格明言尚未解決的界線。

### 如何閱讀

- 先讀第 1 章，理解為何「生成」不是整個產品。
- 第 2 章適合已有 v1 或 v2 心智模型的讀者；它說明何以 v3 不是單純加功能。
- 第 3 章把原則轉成取捨準則；後續章節會反覆引用它。
- 第 4 章是全書的地圖。閱讀後可按目錄跳至相應的後續具名章節。

### 全書目錄

**第一部分　立論與架構**

1. [問題定義、產品意圖與非目標](#第-1-章問題定義產品意圖與非目標)
2. [從 v1 到 v3：由流程計劃走向執行基線](#第-2-章從-v1-到-v3由流程計劃走向執行基線)
3. [設計原則與管治哲學](#第-3-章設計原則與管治哲學)
4. [最終架構與控制平面概觀](#第-4-章最終架構與控制平面概觀)

**第二部分　規範性基礎**

5. 專案清單、輸入驗證與權利邊界
6. 不可變工件、內容定址與譜系
7. 雙層狀態機、閘門就緒度與範圍覆蓋
8. 相依圖、變更分類與精準失效
9. 核准語義：剪輯指紋、證據雜湊與延續規則

**第三部分　創意前期製作與連續性**

10. 參考資料情報、可轉移工藝與受保護表達
11. 視覺聖經、護照與符號化連續性分類帳
12. 鏡頭設計、線框圖、意圖劇本與地區時長預檢
13. 動畫預演與 Gate A：先核准結構

**第四部分　生成、品質與剪輯**

14. 能力路由、預算准入與片段生成
15. 確定性品質、感知驗證、原創性與肖像控制
16. Gate B、規範剪輯、畫面鎖定與本地化交付
17. Gate C、交付套裝與已記錄的降級

**第五部分　受保護發布與營運**

18. 披露、非公開上載、遠端驗證與 Gate D
19. 可靠性、租約、圍欄、重試與復原
20. 可觀測性、平台可攜性、綱要演進與路線圖

**附錄**

A. 詞彙與縮寫　B. 需求識別碼索引　C. 工件與指令詞彙　D. 閘門審閱清單　E. 開放問題登錄

## 詞彙表

| 詞彙 | 本書中的意思 |
|---|---|
| **工件（artifact）** | 不可變、具版本與譜系的媒體或結構化資料輸出；其身分由內容與雜湊支持。 |
| **控制平面** | 不直接產生媒體、但決定甚麼工作可進行、何時可推進、成本是否可承擔及核准是否有效的一組服務。 |
| **配接器（adapter）** | 把穩定的供應商中立合約轉譯為某項工具、模型或平台能力的邊界元件。 |
| **護照（passport）** | 視覺聖經內供重複實體使用的已版本化描述、參考、負面約束及狀態宣告。 |
| **剪輯指紋（edit fingerprint）** | 從規範化剪輯決策計算的身分；它回答「是否同一剪輯」，而非「是否同一個編碼檔」。 |
| **閘門（Gate）** | 人員作出的可稽核授權點。A 核准結構、B 核准鏡頭、C 核准交付、D 授權公開。 |
| **分類帳（ledger）** | 依故事時間傳播實體有狀態屬性的符號模型，用於在生成前找出矛盾。 |
| **降級階梯** | 鏡頭在質素、成本或能力限制下無法達標時，按已宣告次序降低企圖並記錄偏差的路徑。 |

---

# 第 1 章　問題定義、產品意圖與非目標

## 1.1 影片生成的真正難題不是一次推論

一段由模型輸出的片段，並不自動構成可交付的影片。它可能漂亮，卻未必接續上一鏡；可能符合提示，卻未必符合角色、道具與故事時間；可能可播放，卻未必有權使用其參考資料、聲音或肖像；可能已上載，卻未必應被公開。若把這些問題全部交給單一提示、單一模型或最後一次人工看片，製作便會把最昂貴、最難復原的決定延後。

Video Flow 的產品意圖，是把結構化故事線、鏡頭指示與獲准使用的參考資料，轉化為可供發布的多語言影片套裝，同時保留人員的編輯控制。它不把生成模型當成製作系統的記憶或真相來源；持久的真相應是專案狀態、規範剪輯、工件譜系、審閱決定、權利證據與成本紀錄。模型可被替換，這些製作事實不可被遺失。

這個定位帶來四個相互連結的問題：

1. **創意一致性。** 每一鏡都必須實現已核准的敘事目的，同時維持角色、道具、地點、風格和時間關係。
2. **營運可控性。** 生成工作可能昂貴、機率性及可並行；系統須在中斷、重試、版本變更與人員拒絕後安全恢復。
3. **權利、私隱與發布責任。** 能取得資料不等於獲授權使用；合成內容亦不能在未披露、未驗證或未授權公開的情況下流出。
4. **可解釋性。** 製作團隊必須能回答：此鏡為何被選取？它依據哪一版護照？哪一個人批准？修改後哪些核准仍有效？花費了甚麼？

> **設計意圖：把成本移到較早、較便宜、較可逆的地方。**  
> 線框圖、動畫預演、符號分類帳與地區時長預檢的共同價值，不在於取代人員判斷，而在於讓人員在尚未購買高保真生成之前，看見結構性錯誤。

## 1.2 產品承諾的邊界

在規格層面，Video Flow 承諾的是一套受約束的製作流程：輸入須先驗證；權利與同意須先被記錄；視覺聖經和時間線不得隱藏在模型記憶內；付費或遠端最終影片生成不得早於 Gate A；鏡頭須在相鄰脈絡中接受 Gate B；完整交付須經 Gate C；公開可見性須待 Gate D。這些不是便利提示，而是把成本與外部曝露分開授權的制度。

產品亦主張「可修復」而非「每次都完美」。一項拒絕不應迫使整部作品重做；一項護照、時長或中繼資料變更亦不應以猜測方式波及下游。後續的[第 8 章「相依圖、變更分類與精準失效」](#全書目錄)會把此原則落實為可稽核的影響範圍。

## 1.3 非目標：系統刻意不代替誰作決定

Video Flow 不提供自動版權釐清或法律意見，也不規避存取控制、數碼權利管理、付費牆、地理限制或平台保護。它記錄權利依據、限制和證據，讓人員作出可追溯決定；工具能開啟一個 URL，永遠不是授權證明。

它亦不在無監督下創作改變已核准故事的新對白，不進行未經授權的聲音複製、肖像複製或冒充，不對私人個人作開放集識別，不訓練基礎模型，亦不聲稱機率性生成會產生確定性輸出。即時協作編輯、即時影片生成和無人值守的長片創作，同樣不在此規格的承諾內。

最容易被誤解的是「自動化」：自動化在這裏不是自主發佈。它是把可重複、可驗證、可恢復的工作交給系統，同時把故事、身分、權利、聲音、公開可見性和例外決定保留予負責的人。

## 1.4 三種完成，三種責任

Video Flow 把「完成」拆成三層。第一層是**創作完成**：鏡頭實現敘事與連續性意圖。第二層是**技術完成**：時間線、聲音、字幕、封裝與中繼資料可被驗證。第三層是**發布完成**：已上載資產與已核准交付相符、披露已記錄、平台狀態已讀回，且有人授權公開。把三者混成一次「完成」按鈕，正是錯誤發布與無法審計的起點。

---

# 第 2 章　從 v1 到 v3：由流程計劃走向執行基線

## 2.1 三個版本，三種成熟度

Video Flow 的演進不是把同一流程改寫得更長，而是逐步把隱含假設變成可強制的機制。v1 回答「一條有創意意識的 AI 影片流程要做甚麼」；v2 回答「這條流程如何成為可保存、可審閱的製作系統」；v3 則回答「在變更、併發、重試與預算壓力下，它如何仍然按原意執行」。

| 版本 | 核心定位 | 主要建立 | 尚餘缺口 |
|---|---|---|---|
| v1 | 創意實施計劃 | 端到端階段、視覺聖經、多語言交付、量化連續性、早期人工關卡 | 固定分數、供應商傾向與敘述式控制仍過多。 |
| v2 | 製作架構基線 | 需求識別碼、不可變工件、權利控制、OTIO、能力配接器、四閘門、受保護發布 | 可恢復性、失效、併發與預算安全仍主要是宣稱。 |
| v3 | 營運執行基線 | 雙層狀態、依賴圖、核准指紋、租約、託管、分類帳、指令、披露與降級 | 控制平面更複雜，且校準、平台與語音等問題仍待驗證。 |

## 2.2 v1：先把創意生產變成一條可討論的流程

v1 的重要貢獻，是拒絕把影片生成縮減為「輸入故事、輸出 MP4」。它引入結構化故事和鏡頭指示、角色／道具／地點護照、線框圖與動態分鏡、片段挑選、音訊與三語字幕、封裝、中繼資料及審計套件。尤其是 Gate A 的位置：在任何昂貴生成之前核准低保真結構，這個決定一直保留至 v3。

但 v1 把若干實驗起點寫得像普遍真理。例如臉部或圖像相似度的固定閾值，可以提示風險，卻不能脫離專案風格、鏡頭類型和模型版本而成為可靠的生產門檻。v1 又偏向列舉模型和工具；這在市場變動時會讓架構跟著供應商名稱一起老化。

## 2.3 v2：從創意計劃轉向持久的製作事實

v2 的轉折在於將「應該記錄」變成「每個階段交換已版本化的不可變工件」。它為要求提供穩定識別碼，讓測試、品質報告和核准可以指向確切義務；以內容定址和沿革保存產物；以 OpenTimelineIO 作規範剪輯模型，而把渲染工具降為配接器；以能力而非供應商名稱路由生成；並把權利、保留、私隱及上載驗證置入流程。

| 範疇 | v1 的重心 | v2 的制度化改變 | 產生的效果 |
|---|---|---|---|
| 品質 | 固定相似度值 | 經校準的證據與保留集驗證 | 分數不再被誤當作普世真相。 |
| 剪輯 | Remotion 為首選來源 | OTIO 為規範、渲染器為配接器 | 編輯意圖不被單一工具鎖定。 |
| 核准 | 審閱目前輸出 | 核准記錄含範圍、雜湊、審批人、時間與狀態 | 可變檔名不能暗中沿用核准。 |
| 權利 | 使用限制與聲明 | 擷取和發布前的權利／同意關卡 | 可取得資料與可合法使用資料被分開。 |
| 發布 | 最終核准後發布 | Gate C、非公開上載、驗證、Gate D | 上傳與公開曝露被拆開。 |

v2 已經描述冪等性、精準失效、重試和預算上限，但仍留下關鍵問題：二十個鏡頭如何同時處於不同階段？護照在生成中途變更時，誰能阻止過時工作寫回？重新編碼同一剪輯是否必須讓所有核准失效？一個困難鏡頭如何不吞掉整筆預算？

## 2.4 v3：把「應該安全」改成「機制上不能繞過」

v3 的答案是控制平面。專案階段承載閘門與整體授權，鏡頭生命週期承載並行工作；有類型的依賴圖令影響範圍由規則推導；剪輯指紋把「同一剪輯」與「同一檔案」分開；租約、心跳、圍欄權杖與提交時輸入重驗保護並行工作；預算託管和止損在花費前拒絕不安全工作。

| v2 留下的問題 | v3 的明確機制 | 管治含義 |
|---|---|---|
| 全域狀態無法表達鏡頭並行 | 專案階段 + 每鏡頭生命週期 | 一鏡回退，不必推翻其他鏡頭。 |
| 失效只靠範例敘述 | 邊類型、變更類別、傳播矩陣與影響報告 | 修復範圍可預測、可稽核。 |
| 雜湊綁定會誤傷重新編碼 | `edit_fingerprint` + 已審閱內容雜湊 + 編碼雜湊 | 剪輯核准與公開檔案身分各有正確層次。 |
| 感知分數不知故事預期 | 先以符號分類帳求解，再以感知檢查驗證 | 有意狀態改變不會被誤判為漂移。 |
| 上限是顯示數字 | 准入、託管、對帳、逐鏡頭止損與費率卡 | 預算成為執行機制。 |
| 本地化在畫面鎖定後才面對 | Gate A 前量度最長語言地區 | 時長衝突在結構核准前處理。 |
| 上載沒有合成披露規則 | 披露決定與上載前後驗證 | 發布不會漏掉必要的內容聲明。 |

> **演進結論**  
> v3 沒有否定 v1 的創作重心或 v2 的工件化架構；它把兩者保留，並補上令承諾可以在真實操作中成立的執行紀律。

## 2.5 有意保留的未解決性

規格成熟不等於所有不確定性已消失。v3 明確保留原創性上限的校準、分類帳對連續量的表達能力、草稿至最終語音的時長漂移、供應商時長聲明的可信度、無 API 的人工 Studio 步驟、提升約束之間的衝突，以及跨語言唇形同步等問題。這種公開並非缺陷；它防止團隊把假設錯當成已驗證功能。

---

# 第 3 章　設計原則與管治哲學

## 3.1 先核准結構，再核准保真度

Video Flow 把結構視為最值得先投資的事物：故事節拍、鏡頭目的、調度、轉場、時長與語言地區可行性，應在高成本動態生成之前被看見。這不是偏愛粗糙預覽，而是承認任何高保真鏡頭都無法補救一條節奏錯誤、連戲矛盾或語言超時的時間線。

## 3.2 時間線與模型分離；工件與決策可追溯

模型不應成為唯一知道「為何這個鏡頭在這裏」的地方。意圖、時間碼、轉場、音軌、字幕、版本和審閱決定必須存在於規範剪輯與工件譜系中。這讓供應商、模型或渲染器可替換，而不會抹去製作記憶。後續第 6 與第 9 章會把不可變工件和核准綁定分別展開。

## 3.3 本機優先，不等於拒絕遠端能力

本機優先是資料最小化與決策排序：能在本機處理的擷取、正規化、分析、評分、線框圖、時間線與基本語音工作，毋須因方便而外流。遠端或付費能力只在政策容許、私隱條款相容、預算准入通過及 Gate A 已授權後才可使用。這是有邊界的混合式策略，不是排斥品質工具的宣言。

## 3.4 把機率分數當證據，而非判決

感知度量有用，卻必須經專案資料、模型版本和明確錯誤政策校準。v3 更進一步：若「印章在左手」可由故事狀態推導，便不應先花錢生成像素，再從嵌入分數猜測它是否錯誤。符號分類帳先聲明預期，感知檢查才問生成結果是否實現該預期。確定性失敗永遠優先於美學分數；法律風險也不應被平均分數沖淡。

## 3.5 核准與執行分離；人員限制進入可執行詞彙

人員核准的是其實際審閱的範圍、剪輯與證據，不是某個可能被覆寫的檔名。人員意見同樣需要兩種形態：自由文字保留判斷理由；封閉、具類型的指令承載可操作內容，例如選鏡、修剪、重定時、重拍、改護照、降級或刪鏡。這一分離既尊重創意語言，也拒絕讓含糊備註成為不可預測的自動化負載。

## 3.6 發布在最後一刻才變得不可逆

發布不是把檔案搬到平台，而是改變可見性並造成通知、索引、觀看與下游複製等外部後果。故此，Video Flow 先讓 Gate C 核准完整交付，再以私人或非公開狀態上載、讀回平台記錄，最後由 Gate D 針對已上載位元組授權公開。這正是「可逆至最後一項操作」的實踐。

## 3.7 交付誠實的成果

生成不會因無限重試而必然變好。當某鏡無法在預算或質素限制內達標，系統不應暗中放寬故事限制，也不應讓整個發行永遠停滯。已宣告的降級階梯讓團隊以可見、具批准級別和具名偏差的方式，選擇簡化動作、替代覆蓋、以風格幀動畫或刪除鏡頭。誠實不是假裝沒有損失，而是把損失交回可負責地核准的決策層。

---

# 第 4 章　最終架構與控制平面概觀

## 4.1 架構不是一條直線，而是受管治的媒體系統

v3 把持久控制狀態與無狀態媒體工作程序分開。工作程序可擷取、分析、生成、渲染、混音或上載；控制平面則判斷這些工作是否有權發生、是否仍基於最新輸入、是否可花費、產物會影響甚麼，以及何時需要人員承擔決定。這個分工避免了「模型完成了工作，所以專案必然可前進」的錯誤推論。

主要元件可概括如下：

| 層面 | 核心責任 | 例子 |
|---|---|---|
| 體驗與審閱 | 收集輸入、呈示預覽、擷取類型化指令、公開健康狀態 | 專案 API、審閱 UI、操作員介面 |
| 控制平面 | 狀態、閘門、相依、預算、政策、證據與事件 | 協調器、圖服務、分類帳、預算引擎、政策引擎 |
| 媒體與創意工作 | 對工件執行專門處理而不擁有專案真相 | 參考、創意、生成、品質、剪輯、本地化工作程序 |
| 發布與稽核 | 管理外部副作用、讀回驗證、輸出證據 | 發布服務、稽核匯出器、可觀測性服務 |

**設計意圖：** 工作程序可以停止、重試或橫向擴展；控制平面仍能依工件、操作鍵和租約重建甚麼已完成、甚麼已失效及甚麼不得重複收費。

## 4.2 雙層狀態：專案需要管治，鏡頭需要並行

專案階段由接收、參考、設計、結構、生成、剪輯、交付、上載、授權至發布，主要處理閘門、成本類別與曝露程度。鏡頭生命週期則由草稿、設計、線框、動畫預演、條件化、生成、品質檢查、候選、核准至鎖定，並可進入封鎖、降級或刪剪側狀態。

這種分層回答了一個實務問題：某鏡被拒絕，應否令全片所有已核准鏡頭失效？答案是否定的。回退可局部發生；只有推進才受閘控。每一項專案階段推進均以其範圍內鏡頭的彙總條件和完整閘門覆蓋為前提。第 7 章將討論此種覆蓋如何令局部修改既安全又不浪費。

## 內嵌工作流程 SVG

工作流程圖保存在獨立的 SVG 檔案中：

![Video Flow v3 工作流程圖](spec/v3/video-pipeline-workflow.svg)

## 4.3 讀圖：六行不是六個部門，而是六類風險的次序

圖的第一行「管治與參考資料情報」從接收、權利、參考擷取、片段探索、電影分析走到視覺聖經與分類帳初始化。它先問「可否碰觸這些資料」，再問「可從中學到甚麼可轉移的工藝」，最後才建立可用於原創製作的約束。這條次序避免可取得的參考素材在權利、保留或受保護表達未釐清時便被當成生成條件。

第二行「創意前期製作」把敘事意圖落到鏡頭設計與線框圖，並在生成前加入兩個 v3 控制：分類帳預先檢查按故事時間找出未宣告狀態變化；地區時長預檢量度每一個啟用語言地區的草稿語音，按最長者編排動畫預演。第 9 步動畫預演不是影片生成的廉價替身，而是整部作品的結構性審閱物。

第三行由 **Gate A** 開始。這個琥珀色、粗邊框節點核准的是已容納最長語言地區的結構與時間，而非漂亮畫面。Gate A 一旦通過，才可進入風格幀、能力路由、最壞情況成本准入與託管、片段生成以及自動化品質控制。圖中把路由與准入單列，提醒讀者：選到一個能力合適的模型，仍不表示該工作可被花錢執行。

第四行以 **Gate B** 把候選片段放回相鄰鏡頭脈絡中審閱。局部優秀的鏡頭仍可能破壞銀幕方向、節奏或連續性；所以 B 以鏡頭為範圍，然後才進入規範剪輯、畫面鎖定、三語音訊與字幕混音、封裝和中繼資料。

第五行把「交付」與「發布」切開：原創性／肖像／披露篩查、母版品質控制、**Gate C**、非公開上載和遠端驗證依次發生。紅色的上載節點是外部副作用，但仍保持私人或不公開；平台狀態必須被讀回，而不能假定請求成功就是交付正確。

第六行才是「受保護發布」。**Gate D** 綁定已上載檔案的位元組身分，授權可見度改變；公開後仍須驗證並保留回退操作手冊。右側的降級階梯與主線平行，表示它不是錯誤處理後的祕密捷徑，而是已宣告的出口。

## 4.4 圖例與四個閘門：顏色代表授權權限

圖例把工作分為四種：藍色是無創意模型決定的自動化處理；青綠色是代理提出的建議或評析；琥珀色粗框是唯一能授權下游成本或曝光的人員閘門；紅色是會影響外部平台的發布操作。這個配色不是美術分類，而是責任分配：代理永遠提供證據和建議，不能把自己生成的工件升格為批准。

| 閘門 | 核准對象 | 解鎖的後果 | 核心保護 |
|---|---|---|---|
| A | 已具地區時長可行性的動畫預演及結構 | 付費／遠端最終影片生成 | 不為未核准的節奏與故事花費。 |
| B | 放入相鄰鏡頭脈絡的候選片段 | 畫面鎖定與下游剪輯 | 不讓局部好片段破壞全片。 |
| C | 母版、各地區交付、封裝、品質與偏差 | 非公開上載 | 發布前先審閱實際交付。 |
| D | 遠端驗證後的確切上載位元組與披露狀態 | 公開可見性 | 不把不可逆外部曝露混同於傳輸。 |

## 4.5 生命週期帶：每鏡獨立前進，側狀態必須可見

圖底的生命週期帶由 `DRAFT` 經 `DESIGNED`、`BOARDED`、`IN_ANIMATIC`、`CONDITIONED`、`GENERATING`、`QC`、`CANDIDATE`、`APPROVED` 至 `LOCKED`。它刻意與上方專案階段分離：同一時刻，一鏡可以在品質檢查，另一鏡可已鎖定，第三鏡則因權利或預算而封鎖。`BLOCKED`、`DEGRADED` 和 `CUT` 是需記錄擁有人、原因與證據的側狀態，而不是 UI 裏被隱藏的例外。

這條帶亦傳遞一項治理原則：回退廉價，推進昂貴。受影響鏡頭可回到其所屬階段，但不得因為其他鏡頭已向前走便跳過需要重新取得的覆蓋。

## 4.6 控制平面面板：令「流程」成為可執行制度

右側深色面板跨越每一行，表示控制平面不是某個前置步驟，而是全程有效。

- **工作流程協調器**維護專案階段與鏡頭生命週期、閘門就緒、範圍覆蓋、租約、心跳、圍欄權杖及冪等操作鍵。
- **依賴圖服務**以有類型邊和變更類別計算工件是失效、僅需複審還是完好，並區分撤銷核准與僅屬過時的核准。
- **連續性分類帳**在生成前傳播故事時間內的實體狀態，檢出矛盾，並把每鏡預期狀態交給後續感知檢查。
- **預算引擎**按優先次序分配鏡頭額度，以最壞情況成本准入與託管，對帳實際收據，並在止損點停止重試。
- **指令與學習服務**驗證封閉的人工指令、產生影響報告、記錄拒絕原因，並只在人工確認後提升重複問題為可撤銷約束。
- **溯源與披露服務**維護工件雜湊、剪輯指紋、權利與保留、合成媒體披露以及已遮蔽、可驗證的稽核套裝。

面板底部的四項不變量濃縮全圖：核准綁定剪輯指紋及實際審閱內容；Gate A 前不得有付費生成；Gate D 前不得公開。應再加上一項由發布流程強制的含義：未有已記錄合成內容披露決定，不得上載。

## 4.7 拒絕路徑：回到最近的責任擁有者

紅色虛線不是「重新開始」箭頭。Gate A 被拒時，只把受影響鏡頭送回鏡頭設計、線框圖或語言時長工作；自動品質控制可在鏡頭預算和止損內重試，之後必須升級；Gate B 被拒時，只重生成或重選該鏡並使相應時間線範圍失效；Gate C 被拒時，回到擁有缺陷的交付階段；遠端驗證失敗則讓影片維持非公開。這些路徑的共同原則是：拒絕有範圍，修復有擁有人，歷史不被刪除。

## 4.8 降級階梯：不把不可行鏡頭變成不可發布專案

橙色點線把生成、品質和交付階段連到降級階梯。其意義不是降低品質要求，而是公開承認能力、預算與時間的限制。階梯由完整動態生成開始，依序容許簡化動作或縮短時長、改走替代路徑、把已核准風格幀製成慢速動態或視差、以替代覆蓋取代、刪鏡並重定相鄰節奏，最後才升級為重新設計、刪剪場景或承擔風險的製作決定。

每一步都要有最低批准級別，並作為具名偏差寫入交付資料；Gate C 必須看見它們。若決定刪鏡，還要進行敘事審閱，確認原有目的已被別處承擔或被有意放棄。這使發布呈現真實狀態，而非被不透明例外修補的假象。

> **開放問題**  
> 圖表定義的是控制意圖與責任邊界，不是某個既有部署的畫面、隊列或服務拓撲。原創性上限、草稿語音與最終聲音的容忍差、供應商能力漂移、無 API 的平台人工步驟，以及跨語言特寫唇形同步，仍須由後續實作、測試與管治決策處理。

本章完成後，讀者應把 Video Flow 看作一個由媒體工作程序支撐、由控制平面約束的製作制度。下一部分將從輸入、權利與不可變工件開始，逐步把這個制度化為可驗證的合約。

# 第二卷：可執行的控制平面

## 第 1 章　控制平面的工作對象：由敘事輸入到可驗證合約

控制平面不處理「如何拍得好看」的美學判斷；它處理哪些資料可被接受、誰可改動甚麼、改動後哪些證據失效，以及並行工作者何時有資格提交結果。這個分工使媒體處理可由無狀態工作者執行，而專案的真實狀態則由不可變工件、僅附加事件日誌及其可變投影共同建立。v2 已確立此原則；v3 把它擴展為可計算的圖、範圍化批准及併發契約。

### 1.1 專案是全域政策合約

`video-flow/project` 清單不是方便填寫的專案描述，而是全案不變條件及政策的版本化宣告。`IN-001` 要求其至少覆蓋標題、簡介、目標時長、輸出設定檔、主要語言、地區設定、預算政策、保留政策、響度設定檔及披露政策。v3 的專案例子另示範確定性渲染設定檔、交付儲備、止損、費率卡版本、品質重試、原創性上限與本地化調適政策。

這些資料處於 project scope 的原因很直接：若個別鏡頭可靜默改寫輸出設定檔、語言交付承諾或「Gate A 前不可遠端生成」的政策，審批與預算便失去共同前提。要修改這類條件，應建立新的輸出設定檔或政策決定，而不是把例外藏入 shot 記錄。

以下 JSON **按 v3 規格範例節錄及改編**；金額與字串只屬示例，尤其不能脫離費率卡把美元數字視作有效估算（`BUD-007`）。

```json
{
  "schema": "video-flow/project",
  "schema_version": "3.0.0",
  "project_id": "prj_moon_gate",
  "primary_language": "yue-Hant-HK",
  "delivery_locales": ["en", "zh-Hans-CN", "yue-Hant-HK"],
  "target_duration_seconds": 90,
  "output_profiles": [{
    "id": "youtube-16x9-1080p",
    "width": 1920,
    "height": 1080,
    "frame_rate": "24/1",
    "color_space": "bt709",
    "audio_sample_rate": 48000
  }],
  "render_profiles": [{
    "id": "delivery-h264-deterministic",
    "deterministic": true,
    "suppress_encoder_metadata": true
  }],
  "budget_policy": {
    "remote_generation_before_gate_a": false,
    "rate_card_version": "rc-2026-08-12"
  },
  "retention_policy": {"approved_segment_days": 30}
}
```

### 1.2 scene 與 shot：穩定識別與兩種排序

`IN-002` 要求每個 scene 和 shot 都有**不依賴顯示順序**的穩定 ID。`scene_S03` 或 `shot_S03_02` 可作為範例 ID，但規格的重點並非命名格式，而是 ID 不會因剪輯重排而改變。顯示順序是可變的編輯資料；若以它作身分，重排一個鏡頭會錯誤地表現成刪除一個舊鏡頭、再建立一個新鏡頭，損害譜系、批准與影響分析。

來源布局把 scene 放入 `story/scenes.json`，shot 放入 `story/shots.json`，且 shot 以 `scene_id` 歸屬於 scene。不過，規格沒有獨立的 `video-flow/scene` 完整 envelope、欄位集或 cardinality 定義。因此可安全地說 scene 是穩定而可引用的敘事範圍；不可杜撰它已有某套完整 JSON schema。

shot 才是控制平面的最小創作範圍。依 `IN-003`，每個 shot 必須有敘事目的、時序意圖、`when`、`what`、`how`、約束、優先次序及所參照的 entity ID。這把供應商中立的創意合約，與隨模型改變的提示詞或請求格式分開；adapter 負責把穩定合約翻譯成供應商專用請求。

v2 的 shot 已有 `display_order`、時長、敘事目的、`when`／`what`／`how`、約束、參考資料與優先級。v3 增加 `story_time`、head/tail handles、`requires`、`effects`、對白節拍及原創性比較資料，目的不是擴充欄位數量，而是讓控制器在生成像素前找出連戲及時長問題。

```json
{
  "schema": "video-flow/shot",
  "schema_version": "3.0.0",
  "shot_id": "shot_S03_02",
  "scene_id": "scene_S03",
  "display_order": 12,
  "story_time": 12,
  "duration": {
    "target_seconds": 4.5,
    "minimum_seconds": 3.8,
    "maximum_seconds": 5.2,
    "handle_head_seconds": 0.4,
    "handle_tail_seconds": 0.4
  },
  "narrative_purpose": "以克制的推鏡揭示角色已認出物件。",
  "when": "速遞員打開木盒之後。",
  "what": [{
    "entity_id": "char_antagonist",
    "action": "轉向鏡頭",
    "emotion": "冷靜地認出對方"
  }],
  "how": {
    "framing_start": "中近景",
    "framing_end": "近景",
    "camera_motion": "緩慢推近",
    "sound": "風聲底噪後接低音漸強"
  },
  "constraints": ["時代服飾", "不得有現代物件", "不得見到文字"],
  "priority": "hero"
}
```

上例同樣是**規格範例的中文化節錄**，並非要求實作者採用該 ID、語句或鏡頭語言。驗證失敗時，`IN-006` 要求系統指出問題欄位、違反的需求 ID、來源檔案及修正操作；「資料無效」不足以讓操作員安全地修復。

### 1.3 `story_time` 不等於 `display_order`

v2 只明示 `display_order`；v3 以 `IN-007` 新增 `story_time` 序數。兩者回答不同問題：

| 欄位 | 所回答的問題 | 主要使用者 | 改動的典型原因 |
|---|---|---|---|
| `story_time` | 故事世界此刻處於甚麼因果狀態？ | 分類帳、連戲檢查 | 非線性敘事重整、補插因果事件 |
| `display_order` | 觀眾在剪輯中何時看到鏡頭？ | 時間線與編輯 | 節奏、插敘、平行剪輯、回憶段落 |

非線性故事可把後來發生的事件先剪出來。若控制器錯以 `display_order` 傳播角色、道具或地點狀態，回憶段落會反過來「改寫」當前時間的狀態；若反以 `story_time` 排時間線，則會抹去有意的敘事結構。規格因此容許兩值不同，並要求分類帳按 `story_time` 處理。

最小概念例子如下：

| shot | `display_order` | `story_time` | 敘事效果 |
|---|---:|---:|---|
| `shot_flashback` | 3 | 1 | 先展示過去的交接 |
| `shot_present_reveal` | 1 | 8 | 觀眾先看到現在的懸念 |
| `shot_transfer` | 7 | 4 | 在故事內完成道具轉移 |

此表是**概念性例子**。規格要求全序的 `story_time` 供連戲傳播，卻沒有指定它必須用整數、時間碼或特定 ID 編碼。

### 1.4 entity：身分屬性與可變狀態必須分家

`IN-004` 要求每個被 shot 引用的 entity ID，在分鏡生成前解析為角色、道具、地點、服裝項目或主題記錄。`CRE-001` 要求 visual bible 為重複 entity 保存標準描述、已批准影像、負面約束及版本化 passport；`CRE-007` 則要求在 bible lock 前檢查相互矛盾的屬性、孤兒 entity，以及 shot 所引但 bible 中不存在的 entity。

v3 的關鍵收緊是 `CRE-006`：passport 每項屬性必須屬於以下其中一類。

| 類別 | 語義 | 可否由 shot effect 改動 | 例子 |
|---|---|---|---|
| invariant | 定義 entity 身分，絕不容許變更 | 不可；嘗試必須驗證失敗（`LED-006`） | 固有雕刻圖樣、核心角色身分 |
| stateful | 可隨故事推進，但只可經已宣告分類帳 effect 改變 | 可，但須先宣告 domain 與初始值（`LED-001`） | 道具持有人、面具是否除下、地點時段 |

這避免把「角色是誰」和「角色此刻手持甚麼」混為同一種版本標籤。v2 的 `continuity_in/out` 可表示「反派 v3」，卻不能表示「印章必須在反派左手」或「何時由速遞員轉交」。v3 用 `requires` 和 `effects` 把後者明確化。

```json
{
  "entity_id": "prop_jade_seal",
  "variables": [
    {"name": "holder", "domain": ["none", "char_courier", "char_antagonist"], "initial": "char_courier", "kind": "stateful"},
    {"name": "hand", "domain": ["left", "right", "none"], "initial": "right", "kind": "stateful"},
    {"name": "carving_pattern", "domain": ["nine-petal lotus"], "initial": "nine-petal lotus", "kind": "invariant"}
  ]
}
```

此 JSON 為**來源的 `ledger-variable` 範例改編**。來源沒有獨立 `video-flow/entity` 或 passport 的完整 JSON schema；本卷因而只說明其強制語義，不會把範例欄位誤稱為完整實體模型。

### 1.5 reference input：取得權利、保留證據與「沒有結果」

每項外部 reference 的輸入最低資料是來源 URL 或本機路徑、相關性提示、預期用途、權利依據及保留類別（`IN-005`）。控制平面須先通過權利關卡，才可下載遠端 reference 或分析本機 reference（`REF-001`）；工具可以取得資料，不等於擁有使用許可。

reference 的已保留片段還須具備來源中繼資料、選取時間戳記、置信度證據及 SHA-256（`REF-003`）。低置信度或相互衝突的匹配必須由人確認（`REF-004`）；完整下載在片段獲批後，按保留政策刪除或隔離（`REF-006`）。v3 進一步要求保留片段保存原創性基準——影格嵌入、動作特徵、鏡頭語法摘要（`REF-007`）——並把「沒有可用片段」列為可記錄的有效結果（`REF-008`）。後者防止系統為了滿足流程而挑選品質欠佳或不相關的候選項。

來源文件沒有獨立的 reference-input 完整 JSON schema。因此下列只是**概念性輸入形狀**，用以顯示 `IN-005` 的資料責任，不能視為已定義合約：

```json
{
  "reference_id": "ref_turn_reveal",
  "source": {"url_or_local_path": "<受權來源>"},
  "relevance_hint": "研究克制推鏡與轉身節奏",
  "intended_use": "只作可轉移攝影技藝參考",
  "rights_basis": "<已記錄權利依據>",
  "retention_class": "reference-derived-30d"
}
```

### 1.6 intent-script beats：先鎖定意思，再量度語言時長

v3 的 `IN-008` 和 `LOC-006` 規定：每個包含對白的 shot 必須參照 intent-script beat ID，而每個對白 beat 必須錨定到 shot 或時間線範圍。intent script 不是後期翻譯稿；它是 Gate A 前的結構資料，至少承載說話者、意思、情緒、術語、發音備註及錨定位置。來源沒有提供 intent-script 的完整 JSON schema，故這份最小形狀是**按規格操作描述整理的概念例子**：

```json
{
  "beat_id": "beat_S03_02_a",
  "speaker": "char_antagonist",
  "meaning": "你終於把它帶回來。",
  "emotion": "壓抑而確認",
  "terminology": ["月門"],
  "pronunciation_notes": ["專名按專案詞彙讀法"],
  "anchor": {"shot_id": "shot_S03_02"}
}
```

設計理由是本地化的說話時長不會隨字數線性相同。v2 是 picture lock 後才處理語音與字幕，較長譯文可能迫使不自然語速，或重新打開已核准剪輯。v3 改在 Gate A 前，對每個啟用 locale 的草稿翻譯，以已聲明草稿 voice profile 合成並量度時長（`LOC-007`）；取最長 locale 加上既定餘裕作 beat 預算（`LOC-008`）。

當錨定範圍不足，操作員及系統必須按專案已宣告的調適政策，依次使用容許的語速調整、停頓壓縮、handle 延伸及 shot 時長調整；耗盡後必須升級為 length-controlled rewrite（`LOC-009`、`LOC-010`）。不得暗中把語速推至不自然值，亦不得讓畫面超時。這是控制平面要求的可見決定，不是剪輯師事後的隱性補救。

## 第 2 章　不可變工件、內容定址與可回放譜系

### 2.1 工件封套是交換合約，不是媒體本身

每個階段交換不可變、具 schema version 的 artifact；可變 project view 則由 artifact 與 append-only event log 的投影建立。此安排把「媒體位元組」與「誰、以甚麼輸入及設定產生它」連在一起，同時避免可變檔案把過去證據悄悄覆寫。

v2 的 `video-flow/artifact-envelope` 已包含 artifact ID／type、project／scope、建立者與時間、內容 URI、SHA-256、byte length、輸入 artifact IDs、configuration hash、adapter、模型／seed、成本與 retention class。v3 保留核心，並有三個對控制平面重要的收緊：

1. `inputs` 不再只是 ID 列表，而是帶 `edge_type` 及版本的項目，令 lineage 同時成為 typed DAG。
2. `operation_key` 與 `lease` 把產生結果連到冪等操作和有資格提交的 worker。
3. 成本由簡單估算／實際值擴展成 estimated、escrowed、committed、reconciled 等帳務階段，並引用 rate-card version。

```json
{
  "schema": "video-flow/artifact-envelope",
  "schema_version": "3.0.0",
  "artifact_id": "art_01J6R4M8QF3W3R3W8M6QF0XK2A",
  "artifact_type": "reference.segment",
  "project_id": "prj_moon_gate",
  "scope_id": "shot_S03_02",
  "content_uri": "artifacts/sha256/7a/<full-sha256>.mp4",
  "sha256": "<64-hex-character-content-hash>",
  "byte_length": 18420393,
  "inputs": [{
    "artifact_id": "art_01J6R4G88Q69W3FKS4JFN0MX1E",
    "edge_type": "derives",
    "version": 3
  }],
  "configuration_sha256": "<configuration-hash>",
  "operation_key": "<operation-key>",
  "adapter": {"id": "segmenter.local", "version": "3.0.0"},
  "lease": {"holder": "worker-07", "fencing_token": 4192},
  "retention_class": "reference-derived-30d"
}
```

上例是**按 v3 artifact-envelope 範例縮寫及去識別化**；佔位 hash 不能用於驗證。`OPS-001` 補充要求生成 artifact 記錄輸入、設定、adapter、模型、可用時的 seed、時間、成本及 log reference。其設計效果是：內容是否可信不取決於檔名，而可由可重建的上下文和雜湊證據檢查。

### 2.2 SHA-256 內容定址：名稱不是身分

canonical blob 位址採用：

```text
artifacts/sha256/<first-two-hash-characters>/<full-hash>.<extension>
```

同一內容的 SHA-256 相同，因此可共享同一 immutable blob；內容一旦改變，hash 與位址都改變。這不等於 artifact ID 消失：artifact ID 用於範圍、譜系和操作；content hash 回答「是否完全相同位元組」。二者分開，才能同時描述不同 provenance 的相同內容，或同一邏輯產物的不同重建版本。

應避免兩種失敗模式：

- **以檔名當身分。** `final.mp4` 可被覆寫，卻無法回答審批人看過哪一個位元組。
- **以資料夾位置當 lineage。** 把檔案移至另一個儲存後端不應破壞它的內容身分或上游證據。

v3 的 `PLT-001` 也要求 artifact root 可配置為短路徑，並使用支援延伸長度路徑的檔案系統介面；這容許實作把 hash blob 放在短的本機絕對路徑或物件儲存，而不改變合約。來源同時要求 artifact filename 不由使用者 title 推導（`PLT-002`），避免標題帶來平台保留名、長度或字元問題。

### 2.3 儲存布局：可讀投影與不可變證據分離

以下是 v3 明示的邏輯布局。它是**規格所列的 layout**，並非要求所有部署採用本機檔案系統；artifact tree 可以映射至 object storage 而不改變合約。

```text
projects/<project-id>/
  project.json
  rights/
    rights-manifest.json
    consent-records/
  story/
    storyline.json
    scenes.json
    shots.json
    intent-script.json
  ledger/
    variables.json
    solutions/led-<id>.json
  graph/
    edges.jsonl
    impact-reports/imp-<id>.json
  budget/
    envelope.json
    spend.jsonl
    rate-cards/rc-<version>.json
  timeline/
    edit-v001.otio
  reviews/
    approvals.jsonl
    directions.jsonl
    decisions.jsonl
  learning/
    rejections.jsonl
    promoted-constraints.json
  exports/
    previews/
    delivery/
    audit/

artifacts/sha256/<prefix>/<full-hash>.<extension>
events/<project-id>.jsonl
operations/<operation-id>.json
```

這個分層有明確角色：`project.json` 與 `story/` 是人可閱讀及驗證的宣告；`ledger/`、`graph/`、`reviews/`、`budget/` 是控制決定的索引；`artifacts/` 是不可變內容；`events/` 是 append-only 狀態演變；`operations/` 保存操作層的協調資料。v2 的布局已有 project、rights、story、timeline、reviews、exports、artifacts、events 和 operations；v3 新增 intent script、ledger、graph impact reports、budget、directions 及 learning 投影，以支援新的可執行語義。

來源列出 `events/*.jsonl` 和 `operations/*.json`，但**沒有**逐欄定義 event schema、operation persistence schema、snapshot 週期、event replay 次序或物件儲存一致性模型。實作可選擇資料庫或事件技術，但不應把選擇誤寫成既有規格要求。

### 2.4 譜系、事件與修復的關係

譜系回答「此 artifact 從何而來」：輸入、configuration、adapter、模型、seed、operation、lease、成本與 retention。事件回答「project view 為何變成現在這樣」：例如某次合法狀態轉換、批准撤銷或影響報告的建立。兩者不能互相取代：只存 event 無法證明媒體內容；只存 blob 無法說明批准覆蓋何時失效。

當資料或政策改變，正確做法不是直接改舊 envelope 或覆蓋舊 blob，而是建立新 artifact／新投影，再用 typed dependency graph 計算後果。這使 v2 所說的「從最後有效 artifact 恢復」（`WF-002`）在 v3 能保有前因與後果：失敗或被淘汰的候選仍可留作 lineage-complete orphan，而非偽裝成目前有效產物。

## 第 3 章　兩層狀態機與範圍化閘門

### 3.1 為何一個全域狀態不足夠

v2 提供單一 project machine：從 `DRAFT`、`VALIDATED`、`RIGHTS_CLEARED`、`BIBLE_LOCKED`、`ANIMATIC_APPROVED`、`CLIPS_APPROVED`、`MASTER_APPROVED`，直至 `PUBLISHED`，並在問題時進入 `BLOCKED` 再回所屬前態。它已建立「拒絕不刪除 artifact」及 Gate A 至 D 的治理基線。

但是，單一全域狀態無法精確表達「鏡頭 3 已批准、鏡頭 7 正重新生成、鏡頭 12 因權利問題受阻」並存。若把其中一項問題寫成全案 `BLOCKED`，其餘可用工作會被不必要地停住；若忽略它，則會虛假宣稱全案就緒。v3 以 `STA-001` 至 `STA-006` 明定兩層狀態：project phase 管理治理、支出與公開權限；每個 shot lifecycle 管理局部工作。

### 3.2 project phase：全案的授權軌道

下表重述 v3 的 phase contract。每次持久化轉換都必須在表中已宣告，否則失敗並記錄（`STA-002`）。

| phase | 範圍匯總述詞 | gate／證據 | 可前進至 |
|---|---|---|---|
| `P0_INTAKE` | 無 | 權利及綱要驗證 | `P1_REFERENCE` |
| `P1_REFERENCE` | 每個 reference 有獲批片段、無匹配紀錄或豁免 | 分析完整性 | `P2_DESIGN` |
| `P2_DESIGN` | 每 shot 至少 `BOARDED`；bible 已鎖；ledger 乾淨 | bible lock 批准 | `P3_STRUCTURE` |
| `P3_STRUCTURE` | 每 shot 為 `IN_ANIMATIC`；每 dialogue beat 已通過 locale preflight | Gate A | `P4_GENERATION` |
| `P4_GENERATION` | 每個非 `CUT` shot 為 `APPROVED`、`LOCKED` 或獲批 `DEGRADED` | Gate B | `P5_EDITORIAL` |
| `P5_EDITORIAL` | 每個 timeline item 參照 `LOCKED` shot；畫面鎖定 | master QC | `P6_DELIVERY` |
| `P6_DELIVERY` | 每個啟用 locale 的交付套件完整有效 | Gate C | `P7_UPLOAD` |
| `P7_UPLOAD` | 遠端資產存在、非公開、驗證通過 | 披露驗證 | `P8_AUTHORIZED` |
| `P8_AUTHORIZED` | 遠端／本地 ID 與獲批交付相符 | Gate D | `P9_PUBLISHED` |
| `P9_PUBLISHED` | 公開可見性及中繼資料已驗證 | 終止 | — |
| `P_HALTED` | project-wide 政策或預算封鎖存在 | 補救 | 所屬先前 phase |

`P_HALTED` 只適合 project-wide 問題，例如整體預算耗盡或許可撤回。單一 shot 的技術、品質或權利問題應放在該 shot 的側狀態；把局部問題升格為全案暫停，是會損失併行度的操作錯誤。

### 3.3 shot lifecycle：局部進度與明確回退

| 狀態 | 定義 | 允許下一狀態 |
|---|---|---|
| `DRAFT` | shot 合約存在且驗證通過 | `DESIGNED`、`BLOCKED`、`CUT` |
| `DESIGNED` | 描述及運動計劃已獲評論者批准 | `BOARDED`、`DRAFT`、`BLOCKED`、`CUT` |
| `BOARDED` | 所需線框圖存在，ledger 前提成立 | `IN_ANIMATIC`、`DESIGNED`、`BLOCKED`、`CUT` |
| `IN_ANIMATIC` | 已入預演且 locale 時序可行 | `CONDITIONED`、`BOARDED`、`BLOCKED`、`CUT` |
| `CONDITIONED` | style frame 已批准、生成路線可行 | `GENERATING`、`IN_ANIMATIC`、`BLOCKED`、`CUT` |
| `GENERATING` | 一個或多個候選生成中 | `QC`、`CONDITIONED`、`BLOCKED`、`DEGRADED` |
| `QC` | 候選接受確定性與語義檢查 | `CANDIDATE`、`GENERATING`、`BLOCKED`、`DEGRADED` |
| `CANDIDATE` | 至少一候選通過自動檢查，等待人審 | `APPROVED`、`GENERATING`、`BLOCKED`、`DEGRADED`、`CUT` |
| `APPROVED` | 指定 shot 已在 Gate B 獲批 | `LOCKED`、`CANDIDATE`、`BLOCKED` |
| `LOCKED` | 畫面鎖定時間線正參照此 shot | `APPROVED`（按指令） |

`BLOCKED`、`DEGRADED`、`CUT` 是側狀態，並不抹除原來的正常進度語義。每次進入都必須記錄 owner、reason code 與造成該狀態的 evidence（`STA-006`）。`CUT` 另外要求相鄰 shot 已重新計時，恢復時才可回 `DRAFT`；`DEGRADED` 則必須採用已宣告的降級階梯，並具相應最低 approval level（`DEG-001`、`DEG-002`），而且作為具名偏差在 Gate C 可見（`DEG-003`）。

操作員應把側狀態視為可審計工作佇列，而非備註文字：`BLOCKED` 要指派擁有人和補救；`DEGRADED` 要確認偏差可接受；`CUT` 要確認鏡頭敘事目的已在其他位置保留或有意放棄（`DEG-004`）。

### 3.4 readiness 與 coverage：批准必須覆蓋正確範圍

gate 可提出，不等於 gate 已有效。對 gate `G` 的範圍 `S(G)`，v3 以以下 readiness predicate 表達其最少前提：

```text
ready(G) =
  所有 s ∈ S(G) 均處於 Allowed(G)
  AND 沒有阻塞 finding
  AND 所需 evidence 完整
  AND budget invariants 成立
```

批准又是 scope-bound：Gate B 對每個 shot 記錄；Gate A 與 Gate C 對 composite artifact 記錄。phase 只在 approval coverage 完整覆蓋其範圍時保持有效：

```text
coverage(G) =
  已被有效批准覆蓋的範圍項目數 / 範圍項目總數 = 1
```

這正是 `STA-003` 至 `STA-005` 的含義。若 Gate B 後 `shot_S03_02` 回退到 `CANDIDATE`，控制器只撤銷該 shot 的 coverage，不可一併撤銷其他 shot 已有效的批准；但是 coverage 不再為 1，project phase 必須自動回到 `P4_GENERATION`。這個行為同時避免兩種反模式：一是局部改動令全案無故重審，二是全案仍標作生成完成而掩蓋未覆蓋範圍。

## 第 4 章　分類帳、類型化依賴圖與精準失效

### 4.1 連戲分類帳：先證明因果，再產生媒體

`LED-001` 要每個 stateful passport 屬性成為有名稱、domain 和 initial value 的 ledger variable；`LED-002` 允許 shot 宣告 `requires` 前置條件和 `effects` 後置條件。解算器按 `story_time` 傳播：初始化狀態、檢查當前 shot 的 requires、套用 effects，並報出未滿足條件中變數、所需值、實際值與最後設定它的 shot（`LED-003`）。任何 shot order、`story_time`、requires、effects 或 passport state 宣告變更後都必須重跑；乾淨解決方案是線框圖批准前的條件（`LED-004`）。

```text
# 概念性偽碼，按 LED-001 至 LED-006 的規範語義整理
state = initialise_all_ledger_variables()
for shot in shots.sorted_by(story_time):
    for (variable, required) in shot.requires:
        if state[variable] != required:
            report_contradiction(
              shot, variable, required, state[variable], last_set_by[variable])
    for (variable, value) in shot.effects:
        reject_if_invariant(variable)
        state[variable] = value
        last_set_by[variable] = shot.shot_id
    publish_expected_state(shot, state)
```

典型失敗是：印章初始在 courier 右手，某個稍後 `story_time` 的 shot 要求它在 antagonist 左手，但沒有中間 shot 宣告 transfer effect。正確結果不是讓影像評析器猜測這是漂移還是創意選擇，而是在生成前產生矛盾報告。後續感知連戲檢查應接收每 shot 的 expected state，只有生成結果與該預期衝突才算錯誤（`LED-005`）。

### 4.2 從散文式失效到 typed DAG

v2 已列出重要的失效意圖：轉錄稿改動應影響對齊與字幕而非畫面生成；shot 時長改動應影響 timeline、音訊時序、字幕、章節、封裝、master 和 publish approval；passport 改動令相依 style frames／clips 進 impact review；master 改動撤銷 Gate C／D。這些例子有價值，但沒有 edge type、change class 或停止規則，兩個實作很容易得出不同影響範圍。

v3 的 `GRA-001` 至 `GRA-007` 把它變成 deterministic contract：每 artifact 的 typed input 構成無環圖；每次變更先分類；再按 edge type 與 change class 的矩陣求每個 descendant 是 `INVALID`、`REVIEW` 或 `INTACT`。圖必須無環（`GRA-001`），每條邊必須來自已宣告詞彙（`GRA-002`），而每項變更必須先分類（`GRA-003`）。

### 4.3 邊詞彙與變更類別

| edge type | 意義 | 例子 |
|---|---|---|
| `derives` | child 內容由 parent 計算得出 | 正規化代理衍生 reference segment |
| `conditions` | parent 引導 child 生成 | style frame 或 passport 條件化 clip |
| `constrains` | parent 限制 child 內容 | 負面提示、約束清單、政策規則 |
| `times` | parent 只決定 child 時間安排 | shot 時長決定 subtitle cue 界限 |
| `describes` | child 是關於 parent 的報告 | clip 的品質報告 |
| `measures` | parent 是評估 child 的度量 artifact | identity score 所依的 calibration record |
| `contains` | composite child 包含 parent 成員 | timeline 包含 clip |

| change class | 意義 |
|---|---|
| `CONTENT` | 位元組或含義已變更 |
| `TIMING` | 內容不變，但時長或位置已變更 |
| `CONSTRAINT` | 約束、負面提示或規則文字已變更 |
| `METADATA` | 非編輯描述欄位已變更 |
| `POLICY` | 權利、同意、供應商許可或預算授權已變更 |
| `METRIC` | 度量 artifact 或 calibration record 已變更 |
| `IDENTITY` | invariant passport 屬性已變更 |

### 4.4 傳播矩陣：控制平面的可執行判斷表

`X` 表示 `INVALID`，`R` 表示 `REVIEW`，`.` 表示 `INTACT`。下表是 v3 的規範矩陣；不能以「通常相關」的直覺取代它。

| edge type | `CONTENT` | `TIMING` | `CONSTRAINT` | `METADATA` | `POLICY` | `METRIC` | `IDENTITY` |
|---|---:|---:|---:|---:|---:|---:|---:|
| `derives` | X | R | R | . | R | . | X |
| `conditions` | X | R | R | . | R | . | X |
| `constrains` | R | . | R | . | R | . | X |
| `times` | . | X | . | . | . | . | . |
| `describes` | X | R | . | . | . | . | R |
| `measures` | . | . | . | . | . | X | . |
| `contains` | X | X | . | . | R | . | X |

兩個常被誤做的例子說明這張表的價值：

- clip 像素改變經 `times` 邊到 subtitle cue 是 `INTACT`；字幕時間由時長而非像素決定。若 clip 時長改變，才是 `INVALID`。
- calibration record 經 `measures` 邊的 `METRIC` 改動會使 report `INVALID`，不會使被評分 media 失效。重新校準要重算評估，不代表必須無意義地重拍。

### 4.5 影響報告必先於修復

以下偽碼**按 v3 的傳播算法轉寫**。它不是指定程式語言或儲存實作；它說明 `GRA-004` 的規範順序。

```text
function propagate(root, change_class):
    severity = { INVALID: 2, REVIEW: 1, INTACT: 0 }
    impact = {}
    queue = [(root, change_class)]

    while queue is not empty:
        (node, cls) = queue.pop()
        for edge in outgoing_edges(node):
            effect = MATRIX[edge.type][cls]
            if effect == INTACT:
                continue                    # 此支不再向下追溯
            if severity[effect] <= severity[impact.get(edge.child, INTACT)]:
                continue
            impact[edge.child] = effect
            if effect == INVALID:
                queue.push((edge.child, CONTENT))
            # REVIEW 不下傳；尚未有新的 bytes 或含義

    return immutable_impact_report(root, change_class, impact)
```

此算法之所以實用，有三個理由：圖無環、影響嚴重性只會上升、`REVIEW` 不向下傳播。`INVALID` 代表 child 的內容已不可信，因而向下作 `CONTENT` 傳播；`REVIEW` 只表示需要人確認，尚未改變 bytes，若它的下游亦被標記，整個 project 很快變成無法處理的雜訊。人手審查若導致實際更改，該更改才是新的 root change。

`GRA-006` 要求在安排任何修復工作前，先把計算結果寫成不可變 ImpactReport。來源未給出 impact report 的逐欄 schema，故下列是**概念性記錄**，只展示其必備語義：

```json
{
  "impact_report_id": "imp_<id>",
  "root_artifact_id": "art_changed_shot_duration",
  "change_class": "TIMING",
  "effects": [
    {"artifact_id": "art_timeline", "effect": "INVALID"},
    {"artifact_id": "art_subtitles", "effect": "INVALID"},
    {"artifact_id": "art_style_frame", "effect": "INTACT"}
  ],
  "computed_at": "<timestamp>",
  "sha256": "<report-content-hash>"
}
```

此報告令系統毋須掃描全部 history，便可回答 `GRA-007` 的兩個操作問題：「若改這件工件，甚麼會損壞？」以及「甚麼 evidence 支持某項批准？」

### 4.6 具體失效案例與操作員行為

| root 改動 | 圖上關係／結果 | 對批准的處理 | 操作員應做甚麼 |
|---|---|---|---|
| shot duration 改動 | `times × TIMING = INVALID`；timeline、audio timing、subtitles 等受影響 | 覆蓋 invalid artifact 的批准撤銷 | 先看 immutable report，再修復受影響時間範圍與重審 |
| transcript 內容改動 | 語言對齊／subtitle 類後代失效，不應令 image generation 重做 | 只撤銷受影響範圍 | 不要把畫面候選送回生成佇列 |
| passport identity 改動 | 對 conditioned／derived descendants 通常是 `INVALID` 或需 review；`CRE-005` 指出未獲批後代失效、已獲批後代入 impact review | 覆蓋 invalid 的批准撤銷，review 範圍標 stale | 決定是否改 passport；不要用局部 prompt 偷偷掩蓋身份改動 |
| metric calibration 改動 | `measures × METRIC = INVALID`，報告重算 | media approval 不因 metric 自動重拍 | 重跑品質報告，依結果決定是否人工介入 |
| metadata-only 改動 | 多數 edge 為 `INTACT` | image approval 可延續，但 metadata 須另行批准 | 不要把 metadata approval 誤當成畫面批准 |

`GRA-005` 明定：覆蓋 `INVALID` artifact 的批准必須撤銷；覆蓋 `REVIEW` artifact 的批准標為 stale，並必須能以明確、低成本確認解決，而非無端要求完整重審。這把修復工作與審批負擔按實際變更精確分離。

## 第 5 章　批准身分：剪輯、素材與檔案不可混為一談

### 5.1 v2 的 hash-only 基線與其限制

v2 approval record 綁定 artifact hashes、scope、gate、decision、approver、時間、評論與撤銷狀態。此規則對「檔案改了就要重批」很安全，尤其適合公開前的 Gate D；但它混淆兩個問題：審批人是否看過相同**剪輯內容**，以及交付是否為相同**位元組檔案**。例行 encoder 或 muxer 更新可改變 output hash，而沒有改變決策清單或素材。

v3 以 `APR-001` 至 `APR-007` 將身分拆成三層：

| 身分 | 計算根據 | 回答的問題 | 強制綁定範圍 |
|---|---|---|---|
| `edit_fingerprint` | 規範化 edit-decision list 的 hash | 「這仍是同一剪輯嗎？」 | Gate A、B、C |
| `reviewed_content_hashes` | 實際已審素材的 SHA-256 集合 | 「審批人看過的素材仍相同嗎？」 | Gate A、B、C |
| `encode_hash` | rendered file 的 SHA-256 | 「這仍是同一個檔案嗎？」 | Gate D 及交付 evidence |

`WF-009` 因而要求 approval record 有 scope、edit fingerprint、evidence hashes、approver、timestamp、decision、comment 與 expiry／revocation 狀態。

### 5.2 `edit_fingerprint` 的規範化輸入

`edit_fingerprint` 不是取某個 NLE 專案檔案直接雜湊，而是規範化 edit decision list 的 hash。規格要求它包括每個 timeline item（按 track 及 record order）的 shot ID、source artifact hash、source／record in-out、transition、effect／reframe、audio／subtitle refs、影響交付的 marker text、精確有理數 project-time、render profile ID 及 package element order。

它刻意排除 encoder／muxer version、建立或修改 timestamp、absolute filename、不影響輸出的 artifact IDs、review-only marker 和 comment。這個 include/exclude 界線是批准可攜性的核心：若把工具版本放進 fingerprint，無害重新編碼也會偽裝成剪輯改動；若排除 transition 或字幕 reference，實際 editorial change 又可能漏檢。

### 5.3 批准記錄與 carry-forward

下例是**按 v3 approval 範例節錄**：

```json
{
  "schema": "video-flow/approval",
  "schema_version": "3.0.0",
  "approval_id": "apr_<id>",
  "project_id": "prj_moon_gate",
  "gate": "GATE_A_ANIMATIC",
  "scope": {"kind": "project", "shot_ids": null},
  "edit_fingerprint": "sha256:<normalised-edit-hash>",
  "reviewed_content_hashes": ["sha256:<reviewed-source-hash>"],
  "review_render_hash": "sha256:<review-render-hash>",
  "decision": "approved",
  "approver_id": "human_director_01",
  "comment": "已核對時序及 locale headroom。",
  "carried_forward_from": null,
  "stale": false,
  "revoked_at": null
}
```

`APR-003` 規定：若同一 render profile 下重新渲染，而 edit fingerprint 與 reviewed content hashes 均未變，Gate A／B／C 的批准應 carry forward，並把新的 encode hash 加作 evidence。carry-forward 不是把舊記錄改寫；記錄須保留其 origin，使審計者知道批准從何而來。

| 變更 | fingerprint／content 結果 | 批准語義 |
|---|---|---|
| 同 render profile，較新 encoder 重新渲染 | 兩者不變 | A／B／C 延續；記錄新的 encode hash |
| render profile 改變 | fingerprint 改變 | 撤銷相應 scope 批准 |
| 以新片段替換一段畫面 | fingerprint 與 content 均改 | 撤銷相應 scope 批准 |
| trim 一格 | fingerprint 改，content 未必改 | 撤銷；剪輯已改 |
| 編輯描述／tag 文字改動 | 圖像決策未改 | image approval 可延續，但要 metadata approval |
| subtitle 文字修正 | image 不變、subtitle content 改 | image approval 可延續；subtitle approval 撤銷 |
| immutable schema migration | content 與 fingerprint 不變且有 migration link | 可延續，仍受演進規則約束 |

`APR-004` 是不可放寬的保護：任一 reviewed content hash 改變，即使 fingerprint 恰巧相同，也必須撤銷批准。否則替換來源片段可以保留外觀相同的剪輯決策，卻繞過人審。

### 5.4 encode hash 與 Gate D 的刻意嚴格

`APR-005` 要交付渲染用確定性 render profile，固定 encoder、旗標與 metadata suppression，以便未變剪輯盡可能重現相同檔案。若無法 byte-exact 重現，必須有 diff report，且每項差異均在已宣告 non-editorial allow-list（`APR-006`）。

然而 Gate D 不以「同一剪輯」取代「同一檔案」。`APR-007` 要它綁定已上載檔案的精確 `encode_hash`，因為公開可見性是不可逆或高暴露操作。操作員不應因 A／B／C 的 carry-forward 而假定 D 也可延續；D 必須驗證那一個實際公開的 byte sequence。

## 第 6 章　併發安全：租約、圍欄、重驗證與冪等操作

v2 已要求相同輸入、設定、adapter version 與 operation key 的階段具有冪等性（`WF-001`），並在中斷後從最後有效 artifact 恢復（`WF-002`）。但它未指定 stale worker、重複付費請求或飛行中輸入變更如何處理。v3 的 `CON-001` 至 `CON-006` 補上這個併發契約。

### 6.1 有界租約與 heartbeat

一名 stateless worker 認領工作時，租約至少包含：有界 expiry、holder identity、單調遞增 fencing token（`CON-001`）。worker 用 heartbeat 續租；租約到期後，工作可被另一 worker 重新認領（`CON-002`）。

這個設計不假定網絡中斷等於 worker 已停止。舊 worker 可能在 lease expiry 後恢復運行，因而需要下一道防線。來源沒有指定 lease duration、heartbeat cadence、counter 的儲存位置或 token scope；這些都是實作參數，不能在本書改寫為既定數值。

### 6.2 fencing token：拒絕「復活」寫入者

若寫入者帶的 fencing token 小於該 operation 最近一次已接受 write 的 token，artifact write 必須被拒絕（`CON-003`）。概念時序如下：

```text
T0  worker-A 以 token 41 取得 lease。
T1  A 停頓，lease 到期。
T2  worker-B 重新認領，取得 token 42，並成功提交。
T3  A 恢復，嘗試以 token 41 提交。
T4  儲存／協調層拒絕 A：41 < 最近已接受的 42。
```

沒有 fencing，T3 的舊結果可能覆寫已按較新輸入或決定完成的結果。heartbeat 只幫助判斷可否重領；fencing 才阻止過時擁有人事後寫入，兩者不能互相取代。

### 6.3 commit-time revalidation：產生期間的前提會改變

每份工作必須記錄它依據的每個 input version，例如 passport、ledger solution、constraint set、calibration profile；提交前必須重新驗證（`CON-004`）。如果 worker 生成 clip 時 passport 升版，不能只因 lease 仍有效便提交。正確結果是提交失敗、候選作為 lineage-complete orphan artifact 保留、並產生 impact report。這比靜默宣稱舊候選符合它從未見過的新 passport 安全得多。

概念性提交保護如下：

```text
function commit(work, candidate, lease):
    require lease_is_current(work, lease)
    require lease.token >= latest_accepted_token(work.operation_key)
    require all_recorded_input_versions_still_current(work.inputs)
    compare_and_swap_mutable_projection(work.expected_projection_version)
    accept_immutable_artifact(candidate, lease.token)
```

此偽碼表達需求順序，不指定 transaction API。實作可使用 compare-and-swap、ETag 或另一種具版本檢查的資料庫原語；規格只要求 outcome。

### 6.4 樂觀併發控制：投影不能盲合併

不可變 artifact 可多寫少改，但 project phase、coverage、lease view、operation view 等屬 mutable projections。`CON-005` 要這些投影以版本檢查的 optimistic concurrency control 更新；衝突更新必須基於最新 state 重試，不得盲目合併。

「盲合併」的失敗例子是兩個審批動作分別根據同一舊 coverage 計算：一個撤銷 shot A，另一個批准 shot B。若後寫者直接覆蓋，A 的撤銷可能消失，project phase 便不再可信。正確做法是後者偵測版本衝突、重讀投影、在含 A 撤銷的最新狀態重新計算 coverage，再決定合法轉換。

### 6.5 operation key：把重試與「再來一個候選」分開

v3 定義 operation key 的內容語義如下：

```text
operation_key = sha256(
  stage || sorted(input_hashes) || config_hash ||
  adapter_id || adapter_version || attempt_class
)
```

這段是**規格給出的偽碼**。排序後 input hashes 防止同一集合因列出次序不同而產生重複工作；config／adapter version 保證不同執行條件不會錯誤去重；`attempt_class` 尤其重要，它區分「重試同一候選」和「使用者有意要求另一候選」。若缺少它，系統不是拒絕正當的再生成，就是把網絡重試誤作新付費工作。

相同 operation key 的重複請求應返回既有有效 artifact（`WF-001`）。對 paid operation，admission control 與 operation-key check 必須在同一 transaction，讓兩個並行認領恰好產生一個 chargeable request（`CON-006`）。此交易性要求不是優化：若先各自通過預算、後再檢查 key，兩個 worker 仍可能各自向供應商發出付費請求。

### 6.6 外部副作用的意圖記錄

對外部副作用，`WF-012` 加上一層不同於 operation-key 的保護：發 request **之前**持久化帶 idempotency key 的 intent record，重試前按該 key reconciliation。operation key 保護本地階段／付費生成去重；外部 idempotency intent 保護供應商或上載等不可逆遠端效果，二者不可互相替代。上載又需要持久化 resumable session URI，讓中斷傳輸續傳而非建立第二段影片（`DIS-007`）。

來源沒有指定 intent record 的 JSON schema、operation-key 的 canonical serialization、供應商 idempotency header 名稱或 reconciliation API。它們應在實作合約中補足，並維持本章列出的規範語義。

## 第 7 章　需求家族、版本演進與操作邊界

### 7.1 控制平面需求家族索引

| 家族 | 在本卷的控制責任 |
|---|---|
| `IN` | project／scene／shot／entity／reference 輸入完整性與穩定 ID |
| `REF` | reference 權利閘門、證據、保留與原創性基準 |
| `CRE` | visual bible、passport、invariant／stateful 分類 |
| `LED` | story-time 分類帳、前置條件、效果與矛盾報告 |
| `LOC` | intent-script beat 與 Gate A 前 locale 時長預檢 |
| `STA` | project phase、shot lifecycle、側狀態與範圍 coverage |
| `WF` | gate、冪等性、恢復、approval record、外部副作用意圖 |
| `GRA` | typed DAG、變更分類、傳播、impact report、批准 stale/revoke |
| `APR` | edit fingerprint、content／encode hash、carry-forward |
| `CON` | lease、heartbeat、fencing、OCC、commit revalidation、付費去重 |
| `OPS` | artifact 產生證據、日誌與成本記錄 |
| `PLT` | content-addressed 存儲的可配置短路徑與平台安全 |
| `BUD`、`DEG` | gate readiness 中的預算不變條件及已審批降級語義 |

### 7.2 v2 到 v3：不是只加欄位的升級

比較文件指出，v3 保留 v2 的架構意圖，但聚焦於 v2 聲稱而未完全定義的執行及變更機制。主要差異如下：

| v2 基線 | v3 可執行收緊 | 操作意義 |
|---|---|---|
| 單一 project state | project phase + per-shot lifecycle | 不同鏡頭可並行處於不同狀態 |
| 全案 gate 狀態 | readiness predicate + scope coverage | 只撤銷回退 shot 的覆蓋 |
| 以例子描述失效 | typed edges、change classes、matrix、immutable report | 修復範圍可重現且可稽核 |
| approval 綁 artifact hash | fingerprint + reviewed content + render／encode evidence | 無害重編碼可延續，實質改動必撤銷 |
| operation-key 冪等理念 | lease、heartbeat、fencing、OCC、commit revalidation | stale worker 與重複付款不可覆寫目前狀態 |
| `display_order` 為主 | `story_time`、ledger、intent beats | 連戲與多語時長在付費生成前驗證 |

因此 v2 至 v3 需要 project、shot、artifact、approval、critique、budget、direction 和 ledger records 的新增或變更合約；已有工作流程亦須採納 per-shot state、scope coverage、graph propagation 及 commit-time input validation。把 v3 當作「只補幾個 optional 欄位」會令舊的全局 phase、hash-only approval 或無型別 lineage 繼續產生不一致行為。

### 7.3 規格明確保留的實作空白

嚴謹控制平面也必須誠實標明尚待規格化的界線。以下事項未在三份來源文件以完整契約定義：

- scene、entity、reference input、intent-script 的獨立完整 JSON schema；
- event、operation、lease、impact report 的逐欄 persistence schema；
- lease timeout、heartbeat cadence、fencing counter scope；
- OCC 所用 datastore primitive、圖索引策略、event replay／snapshot 策略；
- operation-key 的字串序列化規則；
- stale approval 的低成本確認 UI、角色與授權細節。

這些不是可以忽略的「小細節」，而是實作需另行決定、測試及版本化的合約面。不過它們也不容削弱已明示的結果性要求：輸入變更不能被舊 worker 提交、invalid approval 必須撤銷、review approval 必須可顯式確認、相同付費 operation key 只能產生一個可計費請求，以及所有可持久化狀態轉換必須符合已宣告的狀態表。

# 第三卷：從故事到獲批交付物

> **本卷定位。** 本卷處理影片的「內容生命」：把已獲接納的故事意圖、權利聲明及參考資料，逐步轉化為可審閱、可鎖定、可本地化的交付套件，直至 **Gate C（母版及交付批准）**。第二卷已說明控制平面如何以狀態、不可變工件、相依關係、租約、預算託管及批准綁定強制執行這些步驟；本卷只在需要解釋創作決定的效力時交叉引用，並不重複該等機制的實作細節。Gate D、非公開上載及公開發佈屬下一卷的範圍。

本書採用 v3 作為規範基線。v1 提供了人機協作的創意製作骨架：參考分析、視覺聖經、線框圖、動態分鏡、生成、音訊及包裝。v2 把骨架變成可交付的製作系統：權利不再只是註記，OpenTimelineIO（OTIO）取代單一渲染器成為剪輯真相，品質分數必須校準。v3 則修正三個會直接影響成片的缺口：先以符號帳本解決連戲矛盾、在 Gate A 前量度三語時長、把「過於像參考片」與肖像風險列為獨立的品質缺陷。除非另有明示，本卷所有「必須」均對應 v3 要求。

---

## 第 1 章　製作前提：接收、權利與參考資料管治

### 1.1 為何創作工作不能由「拿到故事」開始

影片工作常見的錯誤，是把故事文件視為已足夠的開工指令。實際上，故事只回答「要說甚麼」，並未回答「可否使用這段參考、這把聲音、這個字型或這個肖像」。若在權利未清楚前下載、分析或送往外部生成服務，後續每個畫面都可能成為不可用的成本。因此，內容流程的第一個產物不是分鏡，而是可審閱的接收報告與權利清單。

### 1.2 接收包：輸入、決定與輸出

| 輸入類別 | 最少內容 | 系統決定 | 輸出 | 失敗／返回路徑 |
|---|---|---|---|---|
| 專案清單 | 標題、主旨句、目標時長、輸出設定檔、啟用語言地區、預算／保留／披露政策 | 輸出是否可由同一畫面鎖定服務、哪些交付物屬必需 | 已驗證清單及設定檔摘要 | 缺欄位、矛盾設定或無法識別的版本：退回建立者修正 |
| 故事、場景、鏡頭 | 穩定 ID、`story_time`、敘事目的、`when`、`what`、`how`、約束、優先級、對白節拍 | 鏡頭可否被設計；非線性敘事的故事順序 | 交叉參照報告、鏡頭清單 | 找不到實體、重複／無序 `story_time`、循環相依：阻擋，不能以猜測補足 |
| 實體及意圖 | 角色、道具、地點、服裝、主題；對白含義、情緒、術語 | 哪些元素要建護照；哪些節拍需做時長預檢 | 實體候選清單、意圖腳本骨架 | 未定義的實體或不清楚的對白：退回故事／鏡頭作者 |
| 參考資料 | URL 或本機路徑、相關提示、預定用途、權利依據、保留類別 | 是否可取得、可作分析還是可重用、能否交給指定供應商 | 參考資料登記項目 | 權利、條款、地域、渠道、期限或私隱不符：封鎖該參考，不以「網址可開」當作許可 |
| 外部素材 | 音樂、音效、字型、標誌、相片、表演者肖像／聲音同意 | 可用媒體、語言、地域、用途及到期日 | 權利及同意證據 | 欠缺同意或授權範圍不足：替換素材、縮小範圍或取得有效證據 |

接收階段的關鍵決定是**用途分級**。每個參考要明確標示為：只供鏡頭語法分析、可用作條件影像、可在最終剪輯重用，或不可使用。預設應是「分析鏡頭工藝，不重用來源片段」。這保留了研究構圖、節奏、光線和鏡頭運動的空間，同時不把第三方片段悄然帶入交付物。

權利清單應至少記錄來源、取得依據、准許用途、地域／渠道限制、到期日、署名、保留期及證據位置。肖像與聲音同意還須列出允許的語言和合成用途。這是 v2 對 v1「合理使用／轉化使用聲明」的必要修正：聲明不是權利結論，系統也不提供法律意見；它只要求負責人作出可追溯、可執行的決定。

### 1.3 參考資料的安全與保留邊界

參考影片的逐字稿、標題、說明、字幕、留言及內嵌中繼資料都是**不受信任資料**。它們可成為搜尋或分析內容，但不能改寫故事、護照或工作指令。媒體處理前亦須檢查 MIME 類型、容器、串流數、時長及可解碼性；工具呼叫使用參數陣列而非 shell 插值。這不只是資安要求：一段帶有惡意文字的字幕若被當成製作指令，可污染後面每個提示詞。

保留決定應在下載前已存在。完整參考檔只是一個暫存分析來源；獲批的最小相關片段才是可保留工件。以專案清單為例，`full_reference_days: 0` 表示在片段核准後立即刪除或隔離完整下載；`approved_segment_days: 30` 只准保存已選片段三十日。日期只是政策例子，**並非通用保留期限**。每次刪除或隔離都要留下證據，否則「最小保留」無法稽核。

### 1.4 接收審查清單

- [ ] 專案、故事、鏡頭、實體及參考文件均通過其版本化綱要。
- [ ] 每個鏡頭有穩定 ID、`story_time`、敘事目的、實體引用及約束。
- [ ] 每個對白鏡頭連到一個意圖節拍；沒有對白也應明確表示。
- [ ] 每個參考已列出預定用途、權利依據、保留類別及相關提示。
- [ ] 音樂、標誌、字型、肖像及聲音的使用範圍已記錄。
- [ ] 外部文字只作資料處理；不會成為指令或未審核提示。
- [ ] 任何權利、私隱或供應商限制已在後續分析／生成前生效。

---

## 第 2 章　由來源到可用證據：接收、正規化與片段發現

### 2.1 正規化代理檔的目的

原始來源往往有不一致的畫格率、像素格式、音訊取樣率、可變時間基或平台插入的中斷。直接對原始檔做場景偵測與嵌入，會讓同一鏡頭在不同機器得出不穩定的結果。因此，先建立分析用代理檔：已知像素格式、畫格率、音訊取樣率及時間基；以媒體探測報告記錄來源串流；再對代理檔雜湊。代理檔不是交付畫質，也不代表可永久保存原始來源。

**輸入：** 已通過權利關卡的來源、局部時間提示、來源中繼資料及保留政策。  
**處理：** 先讀取遠端中繼資料；有明確提示時優先局部擷取；以已批准工具取得；標準化並探測。  
**輸出：** 正規化代理檔、原始探測報告、來源雜湊、時基、取得時間、政策標記。  
**失敗路徑：** 可重試的網絡／供應商錯誤可以有界重試；損毀容器、偽裝副檔名或無效時間碼屬確定性錯誤，必須阻擋並要求新來源；權利撤回則使該來源完全不可用。

v1 已提出一次下載、轉錄、場景偵測與影格抽樣；v2 補上正規化、探測報告和保留政策；v3 保留此低成本本機優先路徑，並要求建立原創性基線，供稍後檢查輸出是否過像來源。

### 2.2 候選片段不是「模型選中的片段」

片段探索要找的是展示所需**工藝**的最小連貫區間，而非宣稱來源的其他部分沒有價值。候選邊界按以下優先序產生：

1. 使用者給出的開始／結束時間、網址時間參數；
2. 來源章節；
3. 偵測到的剪接點與場景邊界；
4. 有語音時的逐字稿句子與說話者輪替；
5. 未覆蓋區域的 3–20 秒重疊視窗。

幾乎相同的候選應合併，但要保留「這個邊界從哪裡來」的來源。抽樣密度應自適應：剪接點、高運動與敘事提示命中的範圍較密，安靜而重複的範圍較疏。標題卡、贊助、標誌、空白、片頭／片尾不是自動刪除，而是懲罰證據；這避免系統誤把故事所需的靜默或文字段落抹走。

### 2.3 可解釋的候選評分

來源規格提供以下起始評分式：

$$
S(c)=0.35V+0.20T+0.15H+0.10A+0.10M+0.10B-P
$$

其中：

| 符號 | 證據 | 問題 |
|---|---|---|
| $V$ | 抽樣影格與鏡頭意圖的視覺語義相似度 | 畫面是否展示所需動作、構圖或場面？ |
| $T$ | 逐字稿與意圖的語義相似度 | 語音／敘述有否提供相關線索？ |
| $H$ | 人工相關提示的一致性 | 是否接近使用者明確指出的部分？ |
| $A$ | 視覺和文字分析的一致性 | 兩種證據是否相互支持？ |
| $M$ | 動作及時間連貫性 | 它是否是可理解的連續示範，而非零散畫面？ |
| $B$ | 邊界整潔度與剪輯可用性 | 能否乾淨地開始、結束及保留把手？ |
| $P$ | 不相關內容、標誌、廣告、空白、突兀截斷的懲罰 | 為何此段不宜被選中？ |

這些權重是**未量度、非通用的起始設定**，不可直接視為自動批准閾值。v1 的做法是以影格相似度加轉錄相似度找高分連續區；v2 增加人手提示、跨模態一致性、懲罰項和保存分項分數；v3 重申「沒有匹配」是有效結果。真正的置信度還取決於第一、二名分差、證據覆蓋率、跨模態一致性及過往校準紀錄。

低置信度或衝突結果的正確輸出不是強選第一名，而是前三個互不重疊候選、聯絡表、逐字稿節錄、時間範圍及分數細目，交由人手確認。MVP 宜採取「所有選段均由人手確認」；只有保留評估已證明指定錯選率內，才可考慮自動接納。

### 2.4 邊界微調與保留片段

獲選區間要同時保住語義與剪輯品質：若動作被截斷，延展至完整動作；若不影響語義，貼近切點或低運動邊界；加入可配置的頭尾把手；精確剪輯時在非關鍵影格附近解碼並重新編碼，近似剪輯才可串流複製。最後驗證首尾可解碼、時間戳單調遞增、代表影格及逐字稿仍指向正確來源時碼。

片段決定的交付物至少包括：來源 ID、來源時間範圍、候選清單及組成分數、置信度理由、逐字稿節錄、代表影格、邊界修改理由、保留片段 SHA-256、保留類別，以及「無匹配」時的明確記錄。完整下載依政策刪除／隔離後，這些證據仍能解釋當初的選擇。

### 2.5 片段探索的審閱清單

- [ ] 直接時間提示優先於章節，章節優先於模型搜尋。
- [ ] 每個候選保留其邊界來源與所有分項分數。
- [ ] 標題、廣告、標誌、空白及片尾作懲罰而非盲目刪除。
- [ ] 低置信度結果顯示三個候選；無匹配沒有被偽裝成命中。
- [ ] 已核准邊界展示完整動作，並有需要的頭尾把手。
- [ ] 已保存段落可解碼、時間單調、具雜湊及來源時碼。
- [ ] 完整來源已按保留政策刪除或隔離。

---

## 第 3 章　讀懂而不複製：電影分析、工藝與受保護表達

### 3.1 分析報告的正確角色

分析的產物不是「更漂亮的提示詞」，而是一份可驗證的觀察報告。每個已批准片段要選出代表性關鍵影格，並附來源時間碼和選取理由；相鄰影格還要有轉場報告。報告把「看到甚麼」與「猜到甚麼」分開標示為**觀察、推論或未知**。例如，可觀察到畫面由中近景推至特寫；可推論鏡頭約為長焦，但沒有鏡頭資料時不可假稱為 85mm。

| 分析欄位 | 應記錄內容 | 常見錯誤 |
|---|---|---|
| 構圖及調度 | 景別、主體位置、負空間、視線、前中後景、銀幕方向 | 把「主角很有張力」當成可用描述 |
| 攝影機與鏡頭線索 | 角度、鏡頭／主體相對運動、景深、透視、疑似焦段 | 把不可從畫面證實的器材列作事實 |
| 光線與色彩 | 主光方向、軟硬、反差、色溫關係、調色、質感 | 只記「電影感」而缺乏可操作證據 |
| 動作與轉場 | 主體軌跡、光流、剪接類型、節奏、環境改變 | 混淆攝影機移動與人物移動 |
| 聲音 | 說話、音樂、效果、環境聲、靜默與節拍位置 | 從參考複製可識別音樂或對白 |
| 不確定性 | 觀察、推論、未知的標籤和理據 | 讓模型填補未知，造成偽精確 |

### 3.2 工藝／表達分區：原創性的第一道門

v3 的核心轉變是把分析結果分成可轉移的**工藝**與不得作為生成條件的**受保護表達**。這不是抽象的法律提醒，而是一個資料流規則：只有工藝分區可以進入鏡頭設計和提示；表達分區只可用於禁止條件與後續篩查。

| 可轉移的電影工藝 | 受保護或高風險表達 | 對下游的操作 |
|---|---|---|
| 景別變化、視線管理、鏡頭語法 | 特定角色外貌、服裝識別、臉孔 | 用抽象鏡頭指示；不轉入護照或提示 |
| 光線比例、反差、光向、色彩關係 | 獨特佈景、極具辨識度的構圖組合 | 改寫為一般空間及光線意圖，避免一比一復刻 |
| 剪接節奏、動作的開始／落點 | 標誌、螢幕文字、專有圖案 | 加入負面約束與 OCR／圖形檢查 |
| 攝影機與主體運動的關係 | 可識別的表演、聲音、音樂、對白 | 用新演出／自有音訊達到同一敘事功能 |

例如，「在角色打開盒子後，以緩慢推近壓縮空間，讓目光先落於畫外再回到鏡頭」是可轉移工藝；「複製某演員的面部轉向、同一枚圖案印章、同一房間中的反射構圖」則是受保護表達風險。鏡頭設計必須保留故事的揭示功能，但要以不同角色設計、場景配置、行動編排和視覺細節實現它。

### 3.3 原創性基線的建立

每個保留參考片段都要保存三類基線：影格／構圖嵌入、動作特徵、鏡頭語法摘要；另保存任何已見文字、標誌及獨特圖形的檢測結果。它們不是為了獎勵生成鏡頭「像參考」，而是使後續系統能提出相反問題：生成結果會否過於接近此來源？

這是 v2 到 v3 的必要反轉。v2 已用相似度量度角色、道具、地點及風格連貫性，但沒有衡量第三方參考相似性。v3 因而在設計階段就限制可用資料，並在生成後把高相似度視為缺陷。原創性上限沒有可信的全球數值；任何上限、特徵權重或自動攔截條件都是**經專案校準前的非通用值**。

### 3.4 分析交付及故障處理

分析完成後，應交付機器可讀關鍵影格／轉場報告、帶來源時碼的聯絡表、工藝／表達分區、原創性基線和可重現資訊（保留片段雜湊、分析配接器版本、設定雜湊）。若分析不能判斷鏡頭、天氣或聲源，應輸出 `unknown`，而非補寫看似專業的虛構資料。若受保護元素已成為原始鏡頭指示的必要部分，返回創意製作人：改寫意圖、取得權利，或移除該參考；分析代理不應自行把風險元素洗白。

---

## 第 4 章　把製作記憶外置：視覺聖經與護照鎖定

### 4.1 視覺聖經解決甚麼問題

影片模型不會跨次生成可靠地記得同一角色、道具或地點。v1 已正確指出，流程本身必須成為記憶；v2 將其變成版本化護照；v3 再把護照屬性分成「不變」和「有狀態」。因此，視覺聖經不是靈感拼貼，而是全片共用的約束資料庫。

每個重複實體至少包含：正規名稱和 ID、標準描述、獲批參考影像／轉面圖、比例和材質、負面約束、使用鏡頭、版本、權利／同意範圍。專案層則包含攝影文法、鏡頭語彙、光線規則、調色板、顆粒／材質、聲音語言、禁止現代物件或螢幕文字等。

### 4.2 不變與有狀態屬性

| 類別 | 例子 | 可否被鏡頭效果改寫 | 檢查方式 |
|---|---|---|---|
| 不變（identity） | 印章的九瓣蓮紋、角色眼色、固定面部特徵、道具基本材質 | 不可 | 若 `effects` 企圖更改，綱要驗證立即失敗 |
| 有狀態（stateful） | 印章持有人／手、面具是否除下、衣物是否破損、地點時段 | 可以，但必須由宣告的效果改寫 | 由連續性帳本按故事時間傳播 |

這個分類避免兩種相反錯誤：把敘事需要的變化鎖死，或讓模型把身份特徵當作可任意漂移。v2 的 `continuity_in/out` 版本標籤可表明「此鏡頭使用道具 v2」，卻無法表明「道具此刻必須在反派左手」；v3 所以改用具值域、初始值、前置條件及效果的表示法。

### 4.3 建立與鎖定流程

1. **抽取。** 從整個故事、鏡頭與合法參考抽取角色、道具、地點、服裝和主題母題；不要只從第一場戲建立護照。
2. **規範化。** 為每項實體寫出正向描述與不可出現事項；將工藝資料轉成專案風格規則，而非複製來源角色設計。
3. **建立證據。** 附上自有或有權使用的角色圖、轉面圖、道具／材質／比例參考、地點版圖和色彩參考。
4. **分類。** 標註每一個屬性為不變或有狀態；後者宣告變數名稱、可接受值域及初始值。
5. **一致性檢查。** 偵測同一護照內矛盾、從未被鏡頭引用的實體、鏡頭引用但聖經不存在的實體，以及權利不匹配的影像。
6. **人手鎖定。** 審閱者核准特定聖經版本。鎖定後，鏡頭設計只能引用它，不能默默修改它。

**輸出：** 已鎖定視覺聖經、護照版本、初始帳本變數、實體引用報告、鎖定批准。  
**失敗：** 角色描述相互衝突、鏡頭引用未定義實體、護照圖無權使用或屬性未分類時，退回聖經編輯；不應帶著「暫定」護照進入生成。

護照修訂仍然可以發生，但必須產生新版本和影響審查。內容層面的修訂可能令未批准條件影像／片段失效；已批准內容至少需顯式審查。此處只需記住創作後果：護照不是可隨意覆寫的 prompt 片段，否則後面鏡頭會在不同「角色真相」下完成。

### 4.4 護照鎖定檢查表

- [ ] 所有鏡頭實體 ID 都可解析至護照項目。
- [ ] 護照影像、聲音、字型、標誌等均有適當權利範圍。
- [ ] 正向描述、負面約束、比例、材質與風格規則不存在內部衝突。
- [ ] 每個屬性已標為不變或有狀態；有狀態屬性已定義值域和初始值。
- [ ] 每項參考驅動的風格規則只採用工藝分區。
- [ ] 已有特定版本的人工鎖定批准。

---

## 第 5 章　先證明故事自洽：符號連續性帳本與感知驗證

### 5.1 兩層連戲，而非一個相似度分數

連戲有兩個不同問題：計劃是否自洽，以及畫面是否實現計劃。前者可在生成前以確定性方式解決，後者才需要昂貴的感知模型與人眼。v1 以固定人臉、道具、場景相似度作為門檻；v2 正確地將它們降為須校準的證據；v3 再加上符號帳本，避免讓感知系統猜測「道具易手是劇情還是錯誤」。

| 層次 | 主要問題 | 輸入 | 輸出 | 執行時機 |
|---|---|---|---|---|
| 符號帳本 | 已聲明狀態是否自洽？ | 初始變數、`story_time`、每鏡頭 `requires`／`effects` | 預期狀態或矛盾報告 | 線框圖批准前、變更後 |
| 感知驗證 | 生成畫面是否符合預期狀態？ | 護照、已選片段、帳本預期狀態、校準設定檔 | 組成證據、發現、排名 | 生成後、Gate B 前 |

### 5.2 帳本資料模型與求解走讀

假設玉印的變數如下：

| 變數 | 值域 | 初始值 | 種類 |
|---|---|---|---|
| `prop_jade_seal.holder` | `none`、`char_courier`、`char_antagonist` | `char_courier` | 有狀態 |
| `prop_jade_seal.hand` | `left`、`right`、`none` | `right` | 有狀態 |
| `prop_jade_seal.carving_pattern` | `nine-petal lotus` | `nine-petal lotus` | 不變 |
| `char_antagonist.mask` | `worn`、`removed` | `worn` | 有狀態 |

鏡頭按 `story_time`，而非畫面播放次序，求解。非線性敘事可把回憶鏡頭放在後面播放，卻仍以其故事時序計算物件狀態。

| 故事時間 | 鏡頭 | `requires` | `effects` | 處理後狀態 |
|---:|---|---|---|---|
| 4 | `S01_04` | 玉印在速遞員右手 | 無 | 持有人＝速遞員；手＝右 |
| 9 | `S02_03` | 玉印在速遞員右手 | `holder=char_antagonist`、`hand=left` | 持有人＝反派；手＝左 |
| 11 | `S03_01` | 反派戴面具 | `mask=removed` | 面具＝除下 |
| 12 | `S03_02` | 玉印在反派左手；面具已除 | `identity_revealed=true` | 條件滿足 |

求解器的基本程序是：初始化所有變數；按 `story_time` 處理每個鏡頭；先比較 `requires` 與目前狀態；再套用 `effects`；拒絕對不變屬性的效果；輸出該鏡頭進入時應看到的狀態。若刪去 `S02_03` 的轉移效果，`S03_02` 會得到以下類型的矛盾：

> `prop_jade_seal.holder`：`S03_02` 要求 `char_antagonist`，實際為 `char_courier`；最後設定者為 `S01_04`；在故事時間 4 至 12 沒有宣告移交效果。

修復選項必須由創作負責人選擇：補上真正發生的移交鏡頭效果、改寫 `S03_02` 的前置條件、重排故事時間，或承認玉印不應在該鏡頭出現。求解器不能自行捏造「有人在畫外把印章交出去」。

### 5.3 感知驗證如何消除假陽性

帳本通過後，`S03_02` 的預期狀態會送給連戲評析員。如果畫面把玉印顯示在右手，發現便可明確寫成「與預期左手矛盾」，而不是含糊的「道具相似度低」。若下一鏡頭的效果明確把玉印交回速遞員，感知層不會把預期易手錯判為漂移。

感知檢查可涵蓋臉部、整體外觀、道具、地點、風格、動作及唇形同步。每份報告要保存構成證據、比較範圍、模型／設定檔版本、置信度及補救建議。v1 的 `0.72` 人臉相似度、`0.78` 整體外觀相似度、`≤35°` 光向差等數字，只可作為實驗起點；它們是**未校準、非通用值**，不得假裝是生產通行門檻。

要把某語義指標升格為阻擋條件，必須以已接納／已拒絕標籤，按實體、鏡頭類型、光線及生成路線分層；在訓練分割選擇符合誤接納／誤拒絕政策的閾值；於保留分割驗證；固定資料集雜湊、模型版本、閾值、混淆矩陣及審閱負責人。任何一項改變都會使校準記錄失效，而不是把既有媒體一律視作錯誤。

### 5.4 何時重跑帳本與何時阻擋

帳本在以下變更後必須重跑：鏡頭順序、`story_time`、前置條件、效果、有狀態護照宣告，以及會改變鏡頭存在與否的剪除／重排指令。矛盾阻止線框圖批准和後續生成；它不是「可平均掉」的美學意見。這是 v3 相對 v2 最省成本的改善：錯誤由生成後的重拍，提前為生成前的文字／資料修正。

---

## 第 6 章　鏡頭設計、線框圖與可執行的審閱意見

### 6.1 鏡頭合約到視覺節拍

鏡頭設計師不得改寫敘事目的或已鎖定護照。其任務是把鏡頭合約轉成可拍、可剪、可評析的開始—中段—結束節拍：主體在哪裡、攝影機如何動、主體如何動、何時改變構圖、何處留給轉場和安全區、聲音意圖如何落點。鏡頭運動與主體運動必須分開表示，否則「推近」和「人物前行」很容易被混成不可控制的生成指令。

| 線框圖套件項目 | 必要內容 | 驗收問題 |
|---|---|---|
| 起始線框圖 | 初始構圖、人物／道具位置、銀幕方向、光向、安全區 | 第一幀能接上前鏡嗎？ |
| 中間線框圖 | 顯著內部變化、動作高點或轉場準備 | 是否足夠描述複雜動作，避免由模型猜中段？ |
| 結束線框圖 | 結束構圖、狀態、下一鏡接點 | 是否提供可剪接的把手與清楚出點？ |
| 運動計劃 | 攝影機曲線、主體曲線、速度／停頓、景深意圖 | 兩種運動有否被獨立定義？ |
| 轉場規格 | 前後鏡關係、剪接／溶接／動作接點、聲音橋 | 是否改變鏡頭的敘事功能？ |
| 連戲依賴 | 護照版本、帳本預期狀態、進出狀態 | 人物、道具、方向及時間是否能成立？ |

每個鏡頭至少有起始和結束線框圖；有顯著內部變化時必須有中間圖。黑白或有限色彩是刻意選擇：此時要審的是結構、節奏與敘事，不是昂貴畫質。

### 6.2 代理角色及不可逾越的界線

| 角色 | 提出／檢查 | 不可做 |
|---|---|---|
| 創意製作人 | 全域意圖、未解決創作衝突、方案取捨 | 批准自己產出的成品 |
| 鏡頭設計師 | 節拍、線框圖、運動、轉場、可剪接把手 | 改敘事目的、改護照 |
| 連戲評析員 | 身份、服裝、道具、銀幕方向、帳本預期狀態 | 覆蓋人手批准、把預期狀態判作錯誤 |
| 攝影評析員 | 構圖、鏡頭、光線、剪接語法、可行性 | 加入未批准故事內容 |
| 動作評析員 | 主體／攝影機運動、時間偽影風險、轉場適配 | 讓確定性媒體失敗通過 |
| 原創性審閱員 | 受保護表達、參考相似風險 | 豁免自己的發現 |
| 技術品質代理 | 媒體與套件的確定性檢查 | 把警告轉為批准 |

評析必須是結構化資料：要求 ID、嚴重度、時間範圍、證據、補救方法、置信度及分數。只有自由文字的「感覺不對」會被拒絕，因為它既不可測試也不可精準套用。

### 6.3 仲裁原則與類型化指令

評論不等於命令。當兩個評析員有衝突，不能以平均分數掩蓋：確定性失敗優先於美學；帳本矛盾優先於感知分數；權利、肖像、故事、聲音及發佈問題交由人手；創意製作人提出方案及兩方理據。自動修訂在設定的嘗試／成本上限停止，預設可取四次品質重試作**專案起始策略，非通用常數**。

人手審閱也要輸入機器可執行的封閉詞彙，而非只留批註。常見指令如下：

| 指令 | 用途 | 對內容流程的效應 |
|---|---|---|
| `ACCEPT`／`SELECT_TAKE` | 接納候選或選取替代 take | 記錄批准或改變鏡頭選擇 |
| `TRIM`／`RETIME` | 修剪或在聲明界限內重定時 | 改變時序，連帶重檢字幕、章節及時間線範圍 |
| `CONSTRAIN`／`REPLACE_CONDITIONING` | 增加約束或換條件影像 | 針對性重設計／重生成 |
| `AMEND_PASSPORT`／`ADJUST_LEDGER` | 修訂護照或故事狀態 | 新版本、影響審查／帳本重解 |
| `RESHOOT`／`SUBSTITUTE` | 付費重拍或用已批准替代素材 | 只影響指定鏡頭及相鄰剪輯範圍 |
| `DEGRADE`／`CUT_SHOT` | 按階梯降低企圖或刪鏡 | 記錄偏差；刪鏡必做敘事審核 |
| `WAIVE`／`ESCALATE` | 記錄有理據的例外或交給負責人 | 不可把法律／權利發現自動豁免 |

自由文字仍應保存，因為它說明創作判斷；但它只能作理據，不能是唯一可操作負載。重複拒絕還要使用受控原因碼，例如 `MOTION_UNNATURAL`、`PROP_IDENTITY`、`PACING_SLACK`、`ORIGINALITY_CEILING`。當同一範圍類別反覆出現同一原因，系統可提出一項待人手確認的專案約束；約束數量必須設上限，避免提示詞無限制膨脹。

### 6.4 線框圖階段的輸出與失敗路徑

**輸出：** 每鏡頭線框圖套件、運動／轉場描述、帳本相依、結構化評析、已選修訂、暫定時長、審閱用時間軸素材。  
**失敗：** 敘事目的丟失，返回鏡頭設計；護照衝突，返回聖經；帳本矛盾，返回故事狀態／鏡頭要求；工藝被改寫成受保護表達，返回設計；評析衝突或重試耗盡，交創意製作人或人手審閱。所有返回都只針對擁有問題的鏡頭／範圍，而不是把全片清空重做。

---

## 第 7 章　先讓三種語言都裝得下：地區時長預檢、動畫預演與 Gate A

### 7.1 v2 的順序缺陷與 v3 的修正

v2 把畫面鎖定放在本地化之前；這對三語作品有結構性風險。同一意思在英語、普通話與粵語所需時長可能不同，若先批准只適合其中一種語言的節奏，後期只能加速語音、讓畫面超時，或重新打開已批准的剪輯。v3 將「量度最長地區版本」前移至 Gate A 前，讓 Gate A 審批的是三語均可實現的時間安排，而非只審最順耳的一版。

### 7.2 意圖腳本與時長預算

每個對白節拍的意圖記錄包括：節拍 ID、說話者、不可改變的意思、情緒、術語、發音備註、錨定鏡頭或時間線範圍。先為每個啟用地區寫草稿翻譯，以意思而非逐字等值為準；用已聲明的低成本草稿聲音量度各節拍的實際時長。

對節拍 $b$，動畫預演所需預算可表為：

$$
D_{\mathrm{budget}}(b)=\max_{\ell\in L}D_{\mathrm{draft}}(b,\ell)+H(b)
$$

其中 $L$ 為啟用的語言地區集合，$D_{\mathrm{draft}}$ 為草稿聲音量得時長，$H$ 是專案設定的餘裕。餘裕比例、草稿聲音和可接受漂移均是**需按聲音與語言實測校準的非通用設定**；它們不應被本書列為全球固定值。

每節拍將 $D_{\mathrm{budget}}$ 與錨定鏡頭或範圍的可用時長比較。溢出時依序處理：

1. 在聲明的界限內調整語速；
2. 在政策允許時壓縮停頓與換氣；
3. 使用鏡頭頭尾把手；
4. 在鏡頭最長時長及時間線允許下延長；
5. 申請受長度控制的台詞改寫，保留意思與情感；
6. 交敘事審核，而非暗中把聲音加速至不自然。

若最終聲音與草稿聲音差異過大，屬已知未解決限制，必須重跑量度與對齊，而不是假設預檢永遠準確。

### 7.3 動畫預演：以低成本審全片

動畫預演由線框圖、暫定運動、轉場、最長地區的草稿語音、字幕、臨時音效與音樂佔位組成，並以 OTIO 描述次序與時長。審閱版可顯示鏡頭 ID 和審閱標記；交付版不可帶此類標記。它回答的問題是：故事是否看得懂、節奏是否成立、連戲是否通順、包裝順序是否合理、最長語言是否裝得下。

**輸入：** 已鎖定護照、通過帳本的線框圖、對白時長報告、轉場與封裝意圖。  
**輸出：** 動畫預演渲染、OTIO 草稿、時長與地區可行性報告、審閱清單、編輯指紋。  
**失敗：** 對白溢出返回意圖腳本／時長調整；節奏或敘事失敗返回鏡頭設計；連戲失敗返回帳本或線框圖；錯誤只重渲染受影響範圍。

### 7.4 Gate A：批准結構，不是批准漂亮畫面

Gate A 是最具成本槓桿的關卡。審閱者應同時看到動畫預演、每鏡頭線框圖、帳本解決方案、三語時長報告及相對預算的預計成本。批准記錄綁定審閱到的編輯指紋、內容雜湊和審閱渲染，而不是一個容易改名的檔案。

| Gate A 決定 | 授權／效果 | 不通過時的精準路徑 |
|---|---|---|
| 批准 | 允許進入風格幀、能力路由及可能付費／遠端最終生成 | — |
| `TRIM`／`RETIME` | 改指定範圍時長，重算地區可行性及動畫預演 | 返回時長預檢／動畫預演 |
| `CONSTRAIN`／重新設計 | 修正構圖、敘事、風格或原創性風險 | 返回指定鏡頭線框圖 |
| `ADJUST_LEDGER`／重排 | 改故事狀態或排序 | 重跑帳本，再重做受影響預演 |
| 拒絕／升級 | 未能在審閱中作出可執行決定 | 停在結構階段，交責任人處理 |

在 Gate A 前，付費或遠端最終影片生成必須不可發生。這是從 v1 的良好慣例，提升為 v2／v3 的政策與預算強制要求。Gate A 不是讓團隊「先試幾段看看」的行政障礙；它是用便宜工件淘汰全片節奏錯誤、狀態矛盾和語言時長失配的最後機會。

---

## 第 8 章　從已批結構到可生成條件：風格幀、能力路由與時長對帳

### 8.1 風格幀的功能與批准

風格幀把已批構圖變成高保真條件，而不是重新發明鏡頭。每鏡頭製作彩色起始、中段及結束畫格（中段僅在需要時），使用護照、線框圖和帳本預期狀態；再評估身份、道具、地點、色調、光線、取景及禁止元素。所有候選保留譜系，獲選畫格才成為生成條件。

風格幀的人工選擇尤其重要：它在付費動態生成前暴露角色漂移、錯手道具、受保護構圖、錯誤光線或不合規文字。v1 有「上色靜態關鍵影格」概念；v2 將條件、成本和譜系明文化；v3 加入帳本預期狀態與原創性比較範圍，令靜態畫面同時是連戲和原創性防線。

### 8.2 能力路由：先排除，再排序

模型名稱不能寫進鏡頭合約，因為供應商、時長支援、私隱條款與成本都會變。每個已批准適配器要聲明輸入類型、最大／最小／量化時長、解析度、畫面比例、畫格率、鏡頭／動作／唇形／角色參考支援、種子行為、保留及訓練條款、地域、成本、逾時、退款與版本。先以硬限制排除不合格者：權利、私隱、地域、時長、解析度、比例、預算任何一項不符，即使畫質分高也不可用。

其後才可使用下列路由形式比較合資格適配器：

$$
R(a,s)=Q(a,s)-\lambda_cC(a,s)-\lambda_lL(a,s)-\lambda_pP(a,s)-\lambda_rU(a,s)
$$

$Q$ 是預測品質，$C$ 是成本，$L$ 是延遲，$P$ 是私隱曝露，$U$ 是不確定性；權重由專案政策設定。它們是**專案決策權重，而非通用推薦數字**。備援順序通常是本機首選、已批准遠端標準、已批准遠端主力、簡化動作，最後才是已聲明降級階梯；絕不可靜默放寬故事約束。

### 8.3 時長對帳：量化輸出必須有固定規則

影片模型常把 4.5 秒要求量化為 5 秒或 4 秒。若沒有政策，團隊會在後期用不一致的方法偷改時長，破壞字幕、章節及 Gate A 審過的節奏。每個適配器因此要聲明時長量化、最短／最長時長與精確時長能力。

若回傳時長偏離目標，按以下順序處理：

1. **在把手內修剪。** 較長片段且頭尾有可剪空間時，優先剪尾；但不可切掉動作高峰。
2. **在界限內重定時。** 只可使用專案已聲明範圍，且重定時後要重跑動作品質檢查。
3. **在鏡頭最大值內延長。** 同時必須符合動畫預演的節拍預算與相鄰鏡頭關係。
4. **改用另一條路由。** 選時長量化較相配的適配器。
5. **發出指令並重新批准。** 超出界限的 `RETIME` 或 `RESHOOT` 是創作變更，必須重審受影響時間軸範圍。

這是 v3 對 v2 的補足：任何未被察覺的時長變更，都不應在「對帳」名義下存活。

### 8.4 風格／路由階段交付與失敗

**輸入：** Gate A 所覆蓋的線框圖與時間線、鎖定護照、帳本狀態、適配器登記冊、費率卡、鏡頭優先級及預算。  
**輸出：** 已批風格幀及候選譜系、供應商中立生成需求、選定路線理由、時長政策、原創性比較集、成本預留或拒絕理由。  
**失敗：** 沒有任何合格適配器時不可硬塞進最近似模型；應選備援、簡化鏡頭或進入降級階梯。若預算不容納最壞成本，不能派送；改候選數、路由或升級決策。若風格幀已像參考表達，回到設計而非用更強模型「修好」。

---

## 第 9 章　生成與候選品質：確定性檢查、經校準證據與 Gate B

### 9.1 生成的最小有用候選集

生成只處理已通過 Gate A、具已批條件、已獲能力准入的鏡頭。候選數量依鏡頭優先級、剩餘額度和預期收益決定；並非每鏡都應盲目生成 2–4 版。每次工作保留清理過秘密資料的請求／回應清單、模型／適配器版本、種子（如支援）、輸入條件版本、實際時長、成本及候選雜湊。若護照、帳本或條件在工作途中改變，候選可保留作譜系完整的孤立物，但不可偽稱符合新輸入。

### 9.2 品質檢查的三道分層

| 層次 | 檢查 | 結果 | 是否可由美學分數推翻 |
|---|---|---|---|
| 確定性媒體 QC | 可開啟、解碼至尾、單調時間碼、串流存在、時長、幀率、像素格式、損壞與安全限制 | 通過／失敗 | 不可 |
| 經校準的語義 QC | 身份、服裝、道具、地點、風格、動作、唇形；參考帳本預期狀態 | 證據、分數、置信度、排名 | 校準前只作風險排序；校準後依政策 |
| 原創性／肖像 QC | 構圖、動作、鏡頭語法、文字／標誌重現；已同意護照與排除清單 | 法律／權利發現與比較證據 | 不可自動豁免 |

確定性 QC 必須先跑。影片不能解碼、幀率不符或時長違約，便沒有理由花錢評估它「很有電影感」。語義 QC 必須保存組件證據，不能只留一個黑箱總分；如未校準，分數只能決定人手先看甚麼。原創性與肖像發現也不可平均為美學分數，因為它們的處理權責不同。

### 9.3 原創性與肖像篩查的具體做法

每個受參考啟發的鏡頭都要與其 `compare_against` 集合中的**每一段**來源比較。檢測覆蓋：近似構圖、畫面構成嵌入、動作特徵、鏡頭語法，以及 OCR／圖形層面的文字、標誌和獨特元素。相似度高於專案上限代表需要重新設計，方向與角色連戲相反；低相似度才是正常。上限值沒有可公開通用的數字，故必須視為**未校準的專案政策值**，並保留比較配對、區域／時間範圍與分數供人工判定。

肖像篩查只做兩種受限比較：與已同意護照比對以確認預期身份；與使用者提供的排除清單比對以避免不想要的相似性。系統不對私人個人進行開放集識別，也不把相似發現自動宣布為某真實人物。發現只會升級為人工法律／製作審閱。

### 9.4 有界重試與誠實降級

品質重試與網絡重試不同：它消耗鏡頭預算，且必須根據預測品質收益才可繼續。到達設定重試數、止損或無改善時，不應無限迴圈。可採用已聲明的降級階梯：先簡化動作或縮短鏡頭，再換路由／條件，之後以受批風格幀做慢移動或視差，改用替代覆蓋素材，最後才在敘事審核下刪鏡或重設計。任何降級均是具名偏差，會進入交付清單和 Gate C；它不是偷偷降低標準。

### 9.5 Gate B：在相鄰鏡頭語境中選片

候選片段本身好看並不足夠。Gate B 將每一候選與至少前一、後一鏡一起渲染，讓人審查方向、光線、動作接點、節奏及故事功能。畫面應分開顯示確定性失敗、美學建議、原創性發現和肖像發現，防止法律風險被「整體分數」沖淡。

| Gate B 決定 | 實際含義 | 後續輸出／失效 |
|---|---|---|
| `ACCEPT` | 指定內容雜湊成為已批准鏡頭 | 記錄鏡頭範圍批准；可進入畫面鎖定 |
| `SELECT_TAKE` | 候選中選另一個版本 | 更新此鏡選擇並重渲染相鄰語境 |
| `TRIM`／`RETIME` | 修正節奏或接點 | 重驗時長與相鄰 OTIO 範圍；可能重審範圍 |
| `RESHOOT`／`CONSTRAIN` | 生成結果不符合計劃 | 只重設計／重生成該鏡；須再過 QC |
| `SUBSTITUTE`／`DEGRADE` | 以已批准替代或降級完成 | 記錄偏差，重審語境 |
| `CUT_SHOT` | 刪除鏡頭 | 敘事審核、重新計時、帳本重解 |

Gate B 的退出條件是每個非 `CUT` 鏡頭都由有效的人手批准覆蓋。v1 已有片段人工審閱；v2 補上「在語境中」和雜湊綁定；v3 令每個鏡頭可獨立回退、以類型指令精準處理，並把原創性／肖像納入審閱而不允許自動豁免。

---

## 第 10 章　畫面鎖定：以 OpenTimelineIO 保存可編輯的真相

### 10.1 為何不是把渲染器檔案當作唯一真相

v1 強烈建議以 Remotion 組裝，因為程式碼易於代理編寫與修改；但 v2 發現把剪輯真相鎖進單一渲染工具會妨礙互通和復原。因此 v2／v3 將 OTIO 定為正規編輯模型，FFmpeg、Remotion 或其他已批准工具只是渲染適配器。這不否定程式驅動圖像；它只要求片段、軌道、轉場、標記、外部媒體引用與時碼有一個工具中立的主記錄。

### 10.2 畫面鎖定步驟

1. 在 OTIO 時間線放入 Gate B 批准的片段、來源入／出點、記錄入／出點、轉場、標記和把手。
2. 套用已批准的速度變更、重新構圖、覆蓋與視覺轉場。
3. 驗證每個項目都指向已批准內容雜湊；沒有未批准媒體或臨時取代檔。
4. 以確定性渲染設定檔輸出審閱與交付畫面；若無法位元重現，必須產生只包含允許非編輯差異的報告。
5. 計算畫面鎖定的 `edit_fingerprint`，凍結 OTIO 版本，並將參與鏡頭標記為 `LOCKED`。

`edit_fingerprint` 概括的是人實際審過的剪輯決定：鏡頭 ID、來源雜湊、入／出點、記錄位置、轉場、效果、重新構圖、音訊／字幕參照、交付標記及封裝順序。它不應包含編碼器版本、檔名或建立時間。這使相同剪輯的無害重新編碼可延續內容批准；但一格修剪、新 take、不同轉場或不同渲染設定檔都會改變應審查的內容。

### 10.3 畫面鎖定的輸出與例外

**輸出：** 版本化 `final.otio`、畫面鎖定渲染、編輯指紋、來源／記錄時間碼對照、媒體批准覆蓋報告。  
**失敗：** 某項引用未經 Gate B 批准，返回選片；時長改動越界，返回時長對帳及受影響審閱；加入新疊加、字幕或轉場而改變交付意義，必須重新建立相關批准覆蓋。只有純中繼資料變更可保留畫面批准，但仍需要相應中繼資料與後續發布批准。

畫面鎖定不表示永遠不能改；它表示後續音訊、本地化、字幕、封裝有一個穩定對齊目標。任何改動都必須明說，不能以重新渲染掩蓋。

---

## 第 11 章　由已鎖畫面產生三語交付：音訊、本地化與字幕

### 11.1 後期的角色：製作，而非重新談判節奏

第 7 章已以最長地區語言預留時間，因此本章應把經批准意圖變成三個可獨立審查的交付版本，而非把不同語言硬塞進畫面。除非專案明確停用，必須提供英語、普通話（簡體字幕）及粵語（繁體中文字幕）聲音與字幕。

每地區的最終腳本都要保留故事事實、角色意圖、術語、名稱和情感節拍。若採用以真人為原型的複製或合成聲音，必須先檢查同意記錄是否允許該語言與用途。沒有同意時，使用獲授權的演員／聲音或改寫製作方案；不能以技術可行性取代授權。

### 11.2 音訊生產鏈

| 步驟 | 輸入 | 主要決定／檢查 | 輸出 | 失敗路徑 |
|---|---|---|---|---|
| 腳本定稿 | 意圖腳本、已鎖畫面、術語庫、發音註記 | 是否保留意思與節拍；是否仍符合時長預算 | 各地區定稿腳本 | 超時：按調整階梯，必要時申請受長度控制改寫 |
| 配音／錄音 | 定稿腳本、聲音同意、角色設定 | 聲音合規、自然度、唇形需要 | 對白 stem | 無同意、發音／表演失敗：替換聲音或回到腳本 |
| 對齊 | 畫面鎖定、對白、節拍錨點 | 語音邊界、口型、停頓、鏡頭切點 | 對齊報告及時間碼 | 對齊不足：微調、使用把手或升級改寫；不可靜默超時 |
| 混音 | 對白、音樂、環境、效果 stem | 48 kHz、聲道、可懂度、削波、相位、靜默、響度 | 每語言混音和 stem | 峰值／響度／可懂度失敗：返回混音 |

每個交付保留 48 kHz WAV 分軌；整體混音要量度並記錄整合響度和真峰值，以專案 `loudness_profile` 為準。例如規格示例中的 `-14 LUFS`、`-1 dBTP` 只屬**專案預設值，非通用混音真理**；目標取決於發布策略和聲音內容。

### 11.3 字幕：從時間碼資料到可讀畫面

字幕來源必須同時產出 WebVTT 與 SRT，使用 UTF-8 並測試格式慣例；WebVTT 有正確標頭，SRT 有可解析的行結束和結尾換行。每個提示：

- 在最終審閱後，開始／結束與語音相差不多於兩個專案影格；
- 最多兩行，並通過各輸出設定檔的安全區與可讀性檢查；
- 普通話採用簡體中文，粵語採用繁體中文；
- 不把文字疊到關鍵人臉、標誌或戲劇資訊；
- 不因切換語言而改變已批准的故事事實。

「每行 42 字元」可作 v1 的排版起點，但中文、字體、裝置與畫面比例差異很大，故它是**非通用建議值**，不可取代實際安全區及可讀性檢查。

### 11.4 本地化交付檢查表

- [ ] 三個啟用地區各有經批准腳本、對白、混音、VTT 和 SRT。
- [ ] 所有聲音使用範圍均有有效同意或授權。
- [ ] 最終語音仍符合 Gate A 時長預算；偏差已按政策處理。
- [ ] 所有混音為 48 kHz，且響度／真峰值已量度記錄。
- [ ] 字幕可解析、按序、無無效重疊、最多兩行並通過安全區檢查。
- [ ] 字幕與語音在兩個專案影格內對齊。

---

## 第 12 章　觀眾面向的完整作品：封裝、章節、縮圖與元資料

### 12.1 封裝是時間線內容，不是最後補上的檔案

影片的觀眾版本由精華／預告、片頭標誌、主要內容、片尾名單、可選彩蛋與最終結尾卡組成。這個順序在 v1 已被規定，v2／v3 要求其出現在獲批時間線而非散落的輸出資料夾。精華只可由已批准鏡頭組成，並服從劇透政策；不可為了宣傳而選取尚未通過 Gate B 的「較好看」候選。

| 封裝元素 | 決定 | 輸出／驗證 | 失敗路徑 |
|---|---|---|---|
| 精華／預告 | 選哪個無劇透時刻、目標時長、文案 | 已批鏡頭子時間線、劇透審查 | 劇透或用到未批鏡頭：重新選取 |
| 片頭標誌 | 標誌版本、時長、音訊、權利 | 前置元素與授權證據 | 權利／聲音不符：替換 |
| 片尾名單 | 名字、署名、可讀速度、字型權利 | 可讀性、拼寫、授權 | 署名或字型問題：修正資料／素材 |
| 彩蛋 | 是否存在、是否在名單後 | 時間線排序 | 破壞節奏／劇透：移除或重剪 |
| 結尾卡 | 視覺、文案、時長、行動呼籲 | 安全區、字型／標誌權利 | 超出安全區或資訊錯誤：修正 |

### 12.2 元資料從已批准事實生成

元資料不可由模型臆測。它只可引用已批准的標題、故事事實、參與者、權利註記、最終時間線及系列資料。交付至少包括標題、短描述、詳細描述、章節、標籤、1280×720 縮圖、語言中繼資料、授權註記、結尾畫面與播放清單建議。

章節由最終時間線生成，並在上載前驗證：首項 `00:00`、至少三項、時間遞增、每章至少十秒。這些是平台規則，不是美學建議。標籤總長度也在上載前按頻道限制檢查，並處理分隔符號與多字標籤引號。縮圖則驗證尺寸、高對比、文字清晰度與安全區；不應把未獲批准的標誌、真人肖像或劇透帶進縮圖。

### 12.3 地區交付方式的誠實選擇

本地化文字元資料和字幕可透過發布介面處理；每種語言的額外音訊軌未必有相同 API 路徑。專案必須在「三個獨立語言上載檔」和「一段影片加人工 Studio 多音訊步驟」中選擇，並根據當前頻道能力矩陣建構套件。沒有 API 的工作要輸出人工操作手冊及核對清單，不可標示為已自動驗證。這是 v3 對 v2「按頻道能力選擇」的具體化。

### 12.4 封裝與元資料輸出

本章輸出封裝時間線、各語言上載母版、縮圖與結尾卡、YouTube JSON／說明文件、章節資料、語言本地化資料和人工 Studio 操作手冊（如需要）。若章節、標籤、描述、縮圖或封裝順序失敗，應返回其擁有階段；不要重生成已批畫面。元資料改動不必使畫面 Gate B 失效，但它會成為 Gate C 交付審閱與後續發布授權的新輸入。

---

## 第 13 章　最後內容防線：母版原創性、肖像、披露與 Gate C

### 13.1 為何逐鏡原創性不足夠

即使每一鏡都沒有過度相似，剪輯順序、動作節奏、連續構圖和音畫關係仍可能在組裝後重建一段過於接近來源的序列。因此，畫面鎖定和封裝完成後，須再對母版運行原創性與肖像篩查。這一輪檢查亦驗證分析階段標為受保護表達的項目沒有在片尾卡、縮圖、字幕或覆蓋層重新出現。

| 篩查 | 比較範圍 | 合格／不合格處理 |
|---|---|---|
| 母版原創性 | 最終序列對每個相關參考的構圖、動作、鏡頭語法、文字、標誌和獨特圖形 | 高相似度或重現受保護元素：附比較配對、分數、區域／區間，交人手重新設計；不得自動豁免 |
| 最終肖像 | 最終影格對已同意護照及用戶提供排除清單 | 非預期相似：升級人手；不作開放集身份判定 |
| 合成內容披露 | 母版是否含生成媒體、是否有例外人手理由 | 有生成媒體預設肯定；否定判定必須有署名理由 |
| 權利重檢 | 音樂、字型、標誌、聲音、地域／期限與最終用途 | 範圍不符或到期：停在非公開交付，替換或重新取得權利 |

披露決定的目的不是替代創作原創性，而是如實告知平台。當母版包含生成媒體，披露值預設為肯定；若人手判斷非逼真的修改或合成不適用，才可作否定決定並記錄理據。可選的外部來源簽署不能取代內部雜湊沿革；如使用，也只可聲稱平台認可的版本。

### 13.2 母版確定性 QC

每個交付母版要解碼至最終畫格，檢查所有串流，並比較已渲染時間線與 Gate B 已批片段雜湊、時長和 OTIO 範圍。母版 QC 至少包括：

- 解像度、固定幀率、像素格式、色彩標籤、編碼設定檔及快速啟動資料；
- 取樣率、聲道配置、語言標籤、整體響度、真峰值、削波、靜默與相位；
- 字幕可解析性、時間、重疊、行數、安全區和語言；
- 黑幀、凍結幀、轉場異常、意外的臨時審閱標記；
- 封裝元素是否剛好一次、順序正確；
- 章節、標題、說明、標籤、縮圖、授權和披露資料是否完整；
- 重渲染是否位元相同，或差異是否全部落在允許的非編輯欄位內。

預設上載格式可為 MP4、H.264 High Profile、AAC-LC、Rec.709 SDR、固定幀率與 faststart；音訊 stem 為 48 kHz WAV，字幕有 VTT／SRT。這是交付設定檔，不表示所有內部母版只能有一種編碼器。1080p 位元率或其他編碼數值如採用，均應由專案輸出設定檔定義與實測，不應把 v1 的建議數字誤述為通用驗收標準。

### 13.3 交付套件：Gate C 審閱的實物

一個可審閱的 v3 交付套件可採用以下邏輯布局：

```text
delivery/<release-id>/
  manifest.json
  deviations.json
  masters/
    picture-master.mov
    upload-en.mp4
    upload-zh-Hans-CN.mp4
    upload-yue-Hant-HK.mp4
  audio/
    en-dialogue.wav
    zh-Hans-CN-dialogue.wav
    yue-Hant-HK-dialogue.wav
    music.wav
    effects.wav
    ambience.wav
  captions/
    en.vtt  en.srt
    zh-Hans-CN.vtt  zh-Hans-CN.srt
    yue-Hant-HK.vtt  yue-Hant-HK.srt
  artwork/
    thumbnail-1280x720.png
    end-card.png
  metadata/
    youtube.json
    youtube-description.md
    localizations.json
  timeline/
    final.otio
    edit-fingerprint.json
  reports/
    media-qc.json
    language-qc.json
    loudness-qc.json
    originality-qc.json
    rights-qc.json
  runbooks/
    manual-studio-steps.md
  audit/
    audit-manifest.json
    approvals.jsonl
    disclosure.json
    artifact-hashes.sha256
```

`deviations.json` 是 v3 重要新增項：它列出每一個已套用降級，讓批准者看見實際交付而非最初的理想分鏡。審計部分應把輸入／權利清單、提示與種子、工具／模型版本、工件雜湊、編輯指紋、評析與人手指令、成本、品質報告、披露決定和批准記錄連起來。

### 13.4 Gate C：批准完整交付，而非只批准 MP4

Gate C 的審閱對象是整個交付清單：畫面、每種語言的音訊、每條字幕、封裝、縮圖、元資料、原創性／肖像報告、披露決定、權利狀態、偏差和最終成本。批准綁定交付的編輯指紋、實際已審內容雜湊和審閱渲染雜湊。

| Gate C 問題 | 必須有的證據 | 拒絕時回到哪裡 |
|---|---|---|
| 畫面是否正確？ | OTIO、Gate B 覆蓋、媒體 QC、最終渲染 | 選片、畫面鎖定或相關鏡頭 |
| 三語是否同步、自然、可讀？ | 腳本、對齊、混音量度、VTT／SRT QC | 本地化／字幕／混音 |
| 封裝和元資料是否完整且真實？ | 封裝時間線、章節／標籤／縮圖驗證 | 封裝／元資料 |
| 是否原創、合規且已披露？ | 原創性、肖像、權利與披露報告 | 鏡頭設計、素材替換、權利補正或人工判定 |
| 降級是否可接受？ | `deviations.json`、敘事審核、成本報告 | 對應鏡頭或製作決策 |

Gate C 拒絕應只返回擁有缺陷的交付階段。若只改一個字幕提示，不應重新生成影片；若原創性問題源於某個鏡頭，則該鏡頭重設計／重拍後，受影響畫面鎖定、本地化、封裝與交付批准需要更新。這種精準修復依賴第二卷的工件圖與批准覆蓋，但本卷的製作原則很簡單：修正必須小到足以保護已獲批准的好工作，大到足以不留下過時交付物。

### 13.5 Gate C 前最終清單

- [ ] 每個非刪除鏡頭都有 Gate B 批准，並由 `final.otio` 正確引用。
- [ ] 三語母版、聲音 stem、VTT 及 SRT 齊全，且通過媒體／語言／響度 QC。
- [ ] 精華、片頭、主片、名單、可選彩蛋、結尾卡只各出現一次並按批准順序排列。
- [ ] 章節、標籤、縮圖、語言中繼資料及授權註記均已驗證。
- [ ] 已完成逐鏡與母版級原創性篩查；所有肖像發現已由人手處理。
- [ ] 合成內容披露有已記錄決定與理據。
- [ ] 權利／同意在最終渠道、地域和有效期內仍成立。
- [ ] 所有降級已寫入具名偏差，沒有被暗中隱藏。
- [ ] 稽核套件可由雜湊、清單、決定和批准重建交付來源。
- [ ] Gate C 批准覆蓋交付的編輯指紋、內容雜湊與審閱渲染。

---

## 第 14 章　跨版本決策索引：為何本卷的順序不能倒置

下表把本卷的主要製作決定放回 v1→v2→v3 的演進中。它既是遷移指引，也是避免把舊版本「看似可行」的簡化做法帶回新管道的檢查表。

| 主題 | v1 基礎 | v2 修正 | v3 最終理由與本卷做法 |
|---|---|---|---|
| 參考資料 | 一次下載、CLIP／轉錄評分、相關片段 | 權利關卡、正規化、來源雜湊與保留 | 保存工藝證據和原創性基線；允許無匹配，不強選 |
| 分析 | 關鍵影格與電影感描述 | 結構化關鍵影格／轉場、觀察與未知 | 額外分開可轉移工藝與受保護表達，限制資料流 |
| 視覺聖經 | 鎖定描述、影像、負面提示作模型記憶 | 版本化護照及影響審查 | 屬性分為不變／有狀態，為帳本提供精確語義 |
| 連戲 | 固定相似度門檻 | 經校準的感知證據 | 先求解 `requires/effects`，再用感知驗證實際畫面 |
| 線框／預演 | 多代理分鏡後 Gate A | OTIO 動態預演、雜湊批准 | 先做三語時長預檢，Gate A 批准最壞情況節奏 |
| 生成 | 特定模型按工作選用 | 能力式適配器與硬限制 | 適配器另須聲明時長量化；固定時長對帳避免暗改節奏 |
| 品質 | 連戲與評審迴圈 | 確定性檢查先行、語義校準 | 新增原創性上限與受限肖像篩查，兩者不可自動豁免 |
| 剪輯 | Remotion 作主要來源 | OTIO 為規範時間線 | 使用編輯指紋區分同一剪輯的重編碼與真正內容變更 |
| 本地化 | 組裝後才做三語 | 畫面鎖定後做三語音訊／字幕 | 時長預檢前移，後期是生產不是被迫救火 |
| 交付審批 | Gate C 最終母版 | 交付套件、私下上載前審查 | Gate C 額外審原創性、肖像、披露和具名降級偏差 |

本卷的因果順序因而不可隨意調換：沒有權利，不能擷取；沒有工藝／表達分區，不能安全設計；沒有護照和帳本，線框圖無法證明連戲；沒有最長地區時長，Gate A 不應批准節奏；沒有 Gate A，不能付費生成；沒有 Gate B，不能鎖畫面；沒有畫面鎖定，不能可靠混音、字幕和封裝；沒有母版原創性、披露、QC 和完整交付套件，Gate C 就沒有可批准的實物。

至此，故事已經成為一套由人手明確批准、由證據支持、可供發布程序使用的多語交付物。下一卷才處理把這套已批准交付物安全地上載、驗證、授權公開，以及在公開後監察與回退。

# 第四卷：受管治的交付、發佈與營運

## 1. 規範界線與證據標記

受管治交付的判斷依賴可核對的支出、母版、遠端狀態、批准、披露與復原證據，而非單次生成成功。除非特別註明，本卷把 `spec/v3/video-flow_hk.md` 視為**規範性設計基準**。這表示其要求識別碼、資料模型、關卡條件及失敗關閉原則，是實作應遵從的目標；它**不表示**已有可執行程式、已接通的供應商帳戶、已校準的模型、已量度的費率或已在真實頻道完成的端對端驗證。v1 是創意製作計劃，v2 建立了持久工件與受防護發布的架構，v3 則補上並行、預算、批准語義、披露、可攜性與營運的執行機制。本卷會明確區分三個層次：

| 標記 | 含義 | 讀者不應作出的推論 |
|---|---|---|
| **已規定** | 規格以穩定 ID、資料結構、狀態條件或流程規則描述的行為。 | 不代表代碼、UI、供應商連線或營運程序已存在。 |
| **應驗證** | 規格要求以測試、校準、試點、收據或人工檢查證明的行為。 | 不可只憑文件例子或單次成功就宣稱已符合。 |
| **尚未證實／限制** | 規格明示未解決的問題、平台沒有 API 的能力，或需要專案決策的項目。 | 不可用推定、自動化宣稱或「通常可行」掩蓋缺口。 |

因此，「可發布」不是單一布林值，而是一條由預算、權利、交付、遠端狀態、批准及披露共同構成的證據鏈。任何一環未能證明時，正確行為是保持非公開、轉交負責人或記錄偏差，而不是以便利為由繼續公開。

---

## 2. 預算管治：由數字顯示變成准入機制

### 2.1 為何全域上限不足夠

v1 提出使用者可設定硬性預算；v2 進一步要求在遠端生成前估算成本，並在超過硬上限前停止。這些要求建立了正確方向，但若系統只把「已花金額」與「上限」相比，則仍會在三種情況失守：同時送出的工作尚未入帳、失敗／逾時工作仍被供應商收費，以及少數困難鏡頭反覆重試而吞噬整個專案的剩餘額度。

v3 的 `BUD-001` 至 `BUD-008` 因而要求分層預算封套（budget envelope）、託管（escrow）、准入控制（admission control）、每鏡頭止損（stop-loss）及來自實測收據的費率卡（rate card）。這是一項會計與工作排程規則，不是儀表板上的預測數字。

專案清單至少應宣告：

- `hard_limit`：不得突破的專案總成本；
- `delivery_reserve_fraction`：專為渲染、音訊、本地化、字幕、品質修復及發佈保留的比例；
- `priority_weights`：`hero`、`supporting`、`broll` 等鏡頭優先次序權重；
- `shot_stop_loss_multiple`：每鏡頭容許成本上限的倍數；
- `rate_card_version`：所有估算所依據的版本化實測費率卡；
- `remote_generation_before_gate_a: false`：Gate A 前禁止遠端最終影片生成的機械化策略。

可分配予生成的預算不是整個硬上限，而是：

$$
\mathrm{allocatable}=\mathrm{hard\_limit}\times(1-\mathrm{delivery\_reserve\_fraction})
$$

若以鏡頭優先次序分配，鏡頭 $s$ 的基礎封套可以按下式推導：

$$
\mathrm{envelope}(s)=\mathrm{allocatable}\times
\frac{w_{\mathrm{priority}(s)}}{\sum_{t\in\mathrm{shots}}w_{\mathrm{priority}(t)}}
$$

這並不表示每個鏡頭必須花盡其封套；它只表示一個 `hero` 鏡頭不應在沒有明確政策的情況下，與一段可替代的 `broll` 爭奪同一筆未區分的餘額。封套重分配、提高止損倍數或動用交付儲備，都應是已記錄的政策決定，而非工作者靜默改寫的數字。

### 2.2 託管與准入控制

每項付費操作在送往供應商前，必須使用**最壞情況成本**檢查兩個條件：

$$
\mathrm{escrowed}(s)+\mathrm{worst\_case}(j)\leq\mathrm{envelope}(s)
$$

$$
\mathrm{escrowed}_{\mathrm{project}}+\mathrm{worst\_case}(j)\leq\mathrm{allocatable}
$$

其中 $j$ 是擬派送工作。`BUD-004` 指出，除非供應商合約另有可驗證條款，最壞情況必須假定逾時和失敗同樣收費。以「大概會退款」作預算基礎，會令預算控制在最需要它的故障情況下失效。

支出狀態至少包含下列五種；每次狀態轉移都要附操作鍵、工件範圍、時間戳記、費率卡版本及證據來源：

| 狀態 | 定義 | 何時可用 | 不可做的事 |
|---|---|---|---|
| `estimated` | 由費率卡與工作參數推導的預測。 | 規劃與路由前。 | 不能當作已付款或可用餘額。 |
| `escrowed` | 為最壞情況成本預留的額度。 | 准入通過、尚未派送。 | 不可再被另一個並行工作重複使用。 |
| `committed` | 供應商已接受可能計費的請求。 | 已取得供應商接受證據。 | 不可因本地工作者崩潰而自動視為免費。 |
| `reconciled` | 與供應商收據或可核對帳務匹配的實際成本。 | 收據可取得後。 | 不可把無收據的估算偽裝成實際成本。 |
| `released` | 完成、取消或過期租約後釋放的未使用託管。 | 已確認不會再產生該部分費用。 | 不可在仍有活動請求時釋放。 |

在同一交易邊界內，准入檢查、`escrowed` 記錄與操作意圖須一併建立。否則兩個工作者可同時讀到相同餘額，各自認為可用，並造成兩次可計費請求。這與 `CON-006` 的「同一付費操作鍵剛好一個可計費請求」相連。

### 2.3 逐鏡頭止損與降級關係

`BUD-005` 禁止單一鏡頭累計支出超過其止損倍數。到達止損並不等於刪除鏡頭，也不等於自動接受低質輸出；它必須停止品質重試，轉為人工升級或進入預先聲明的 `DEG-*` 降級階梯。這點很重要：重試是花費，降級是敘事與交付決策，兩者不能混為同一個「再試一次」按鈕。

建議在操作面板顯示下列鏡頭層級資料：

| 欄位 | 用途 |
|---|---|
| `shot_id`、`priority`、目前生命週期狀態 | 判斷工作是否仍值得投入。 |
| `envelope`、`stop_loss`、`escrowed`、`committed`、`reconciled` | 區分可用額度、已承擔金額及已知實際成本。 |
| `quality_retry_count` 與暫時性重試次數 | 防止把網絡重試誤算成品質改善，或反之。 |
| `rate_card_version`、路由器選擇及替代路徑 | 讓成本差異可被事後解釋。 |
| 下一個 `DEG` 步驟及最低批准級別 | 確保止損後的行動不是臨時決定。 |

### 2.4 費率卡：只能量度，不能想像

`BUD-007` 禁止以硬編碼貨幣常數作估算。費率卡應按適配器、能力、地區、輸出長度、解像度、候選數、可能的逾時收費與本機硬件設定檔儲存至少：單位成本、觀察到的失敗率、中位數／p95 延遲、本機 GPU 秒數、峰值記憶體和收據來源。

v1／v2 中「精製 60 秒作品低於 USD 25」可保留為示範專案的 `hard_limit`，但不是可移植的成本承諾。沒有對應 `rate_card_version`、樣本量和收據對帳，該數字只是佔位值。真正可驗證的主張應是：「此專案在指定費率卡、指定輸出設定檔及指定樣本下，估算與收據的差異在已聲明容差內。」

### 2.5 已規定、應驗證與未證實

| 範圍 | 已規定 | 應驗證 | 尚未證實／限制 |
|---|---|---|---|
| 預算 | 封套、儲備、最壞情況准入、託管、止損及按範圍報告。 | 並行准入只產生一筆計費、託管洩漏可修復、收據能對帳。 | 沒有任何通用費率或保證成本。 |
| 路由 | 硬性私隱、權利、時長和預算限制先於品質排名。 | 適配器聲明是否與實際輸出、延遲、取消及退款行為相符。 | 供應商可未經通知改變價格、能力或條款。 |
| 止損 | 超過鏡頭封套時必須升級並提供降級選擇。 | 每個 `DEG` 路徑是否真的可在目標工具鏈產生可接受輸出。 | 「可接受」仍需人員敘事與美學判斷。 |

---

## 3. 權利、同意、私隱與不受信任內容

### 3.1 權利記錄是關卡，不是附註

`RGT-001` 至 `RGT-003` 將權利與同意放入政策引擎。每個參考資料、最終來源片段、音樂、音效、字型、標誌、肖像和合成／複製聲音，均應有可追溯記錄。該記錄需表達取得依據、允許用途、地域、渠道、到期日、署名、保留期限和限制的語言／用途。資料可由人員輸入，但關卡判斷不可只依賴自由文字。

最低限度的權利項目可寫成：

```json
{
  "asset_id": "music_theme_01",
  "kind": "music",
  "rights_basis": "licensed",
  "evidence_ref": "rights/license-2026-001.pdf",
  "permitted_uses": ["youtube-public"],
  "territories": ["worldwide"],
  "channels": ["channel_main"],
  "expires_at": "2027-08-19T00:00:00Z",
  "attribution_required": true,
  "retention_class": "project-final-365d"
}
```

其用途不是讓系統作出法律意見；規格明確把自動版權清權和法律判斷列為範圍外。其用途是令系統在缺少人員提供的有效證據、授權到期或發布渠道不符時失敗關閉。可下載、可播放、可由 `yt-dlp` 取得，均不是獲授權使用的證據。不得繞過存取控制、數碼權利管理、付費牆、地理限制或平台保護措施，亦不得把已驗證 Cookie 用在原來獲批範圍以外。

### 3.2 同意、肖像與合成聲音

人物相關資料至少分為三類，且不得混用：

1. **已同意的肖像護照**：用於確認生成角色是否符合已授權的身分／角色設定；
2. **使用者提供的排除清單**：用於發現不應意外相似的身份；
3. **聲音同意紀錄**：記錄可使用的說話者、允許語言、允許用途、期限與撤銷條件。

`ORG-003` 的肖像篩查範圍刻意狹窄：不得對私人個人作開放集識別，也不得維護一般公眾身份資料庫。命中排除清單或缺少同意，應產生人工法律／權利審查發現，而非對真實人物作自動斷言。任何以某人為原型的聲音複製或合成，必須在第 14 階段交付品質語音前再核對同意範圍，因為「可以作內部試音」不必然等於「可以在全球公開發布」。

### 3.3 私隱與供應商邊界

本地優先不是口號，而是資料流政策。參考影片、擷取影格、轉錄、護照、提示、聲音樣本與中間資產，只有在專案私隱政策、權利清單及已批准供應商能力同時允許時才可離開本機。適配器登記冊必須聲明其保留、訓練用途、地區、輸入種類與安全條款；路由器在比較品質前先剔除不合資格路線。

可落地的資料分級如下：

| 分類 | 例子 | 預設處理 |
|---|---|---|
| `local-only` | 未公開參考影格、聲音樣本、身份護照、原始逐字稿。 | 不可送往遠端適配器；受保留政策控制。 |
| `remote-approved` | 已按政策去識別化、已獲供應商批准的風格條件。 | 只可送往明確列入登記冊的適配器；記錄請求清單。 |
| `public-delivery` | Gate C 批准的母版、公開中繼資料、披露決定。 | 只可經 Guarded upload 流程上載。 |
| `secret` | OAuth refresh token、API token、已驗證 Cookie、供應商標頭。 | 只在秘密儲存與發佈服務使用；不得寫入提示、日誌、metadata 或 audit。 |

`OPS-003` 不是「盡量遮蔽」的建議，而是禁止秘密出現在提示、日誌、中繼資料套件與稽核匯出的要求。遮蔽規則本身需要金絲雀測試：故意注入一個只應出現於秘密儲存的測試值，再檢查結構化日誌、錯誤訊息、工件封套、審核匯出與客服／操作員視圖均沒有該值。

### 3.4 不受信任內容與提示注入邊界

外部媒體的標題、描述、字幕、轉錄、留言、檔名與模型輸出全都是資料，不是控制指令。這條規則同時防止提示注入、命令注入與檔案系統逃逸。系統應採取下列防線：

- 將外部文字封裝為具來源與信任等級的資料欄位，絕不直接串接到系統提示或工作流程控制文字；
- 以結構化 JSON 合約接收代理輸出；只接受已知欄位、枚舉值與範圍；
- 在媒體分析前檢查 MIME、檔案副檔名、容器、串流數目、時長、像素上限及可解碼性；
- 以受限檔案系統、網絡策略、記憶體限制及逾時執行下載器、轉碼器與剖析器；
- 所有子程序呼叫以引數陣列傳遞，永不進行 shell 插值（`PLT-004`）；
- 停用不受信任下載器外掛與遙距元件，除非其被明確批准；
- 在任何人手介面清晰顯示「外部內容」，防止操作員把來源文字誤認為系統指令。

一個關鍵界線是：模型可以就影片內容提出「觀察、推論或未知」，但無權透過輸出文字改寫狀態、核准工件、釋放託管或公開發布。這些副作用只能由工作流程引擎在已驗證合約與人員關卡下執行。

### 3.5 原創性篩查與權利不同，但必須相連

權利清單回答「是否獲准使用來源」；`ORG-001` 至 `ORG-005` 回答「生成內容是否過於接近受參考啟發的來源」。兩者不可互相取代。即使可以分析一段參考影片，生成鏡頭仍須按 `originality.compare_against` 與相關片段比較構圖、動作特徵、鏡頭語法、文字、標誌與獨特圖像元素；高於專案上限的相似度是需要重新設計的缺陷，而不是成功的風格匹配。

此上限沒有可信的通用預設。它必須以「可接受地受啟發」與「過於接近」的已標註對照集合校準，並把比較組合、分數、區域／時間段與人員決定寫入稽核套件。組裝後的母版要再篩查一次，因為多段各自不相同的鏡頭，可在順序與節奏上重建一段受保護的參考序列。

---

## 4. 交付套件、批准證據與稽核鏈

### 4.1 交付不等於一個 MP4

可修復、可重新發布的產品不應只留下單一上載檔案。Video Flow 的交付套件把時間線、母版、地區版本、音訊分軌、字幕、圖像、中繼資料、報告、操作手冊與稽核資料分開，使平台設定或字幕修正不必重新生成創意鏡頭。

規範邏輯布局如下；實際儲存可對映至本機內容定址檔案系統或 S3 相容儲存，但不應改變工件合約：

```text
delivery/<release-id>/
  manifest.json
  deviations.json
  masters/
    picture-master.mov
    upload-en.mp4
    upload-zh-Hans-CN.mp4
    upload-yue-Hant-HK.mp4
  audio/
    en-dialogue.wav
    zh-Hans-CN-dialogue.wav
    yue-Hant-HK-dialogue.wav
    music.wav
    effects.wav
    ambience.wav
  captions/
    en.vtt
    en.srt
    zh-Hans-CN.vtt
    zh-Hans-CN.srt
    yue-Hant-HK.vtt
    yue-Hant-HK.srt
  artwork/
    thumbnail-1280x720.png
    end-card.png
  metadata/
    youtube.json
    youtube-description.md
    localizations.json
  timeline/
    final.otio
    edit-fingerprint.json
  reports/
    media-qc.json
    language-qc.json
    loudness-qc.json
    originality-qc.json
    rights-qc.json
  runbooks/
    manual-studio-steps.md
  audit/
    audit-manifest.json
    approvals.jsonl
    disclosure.json
    artifact-hashes.sha256
```

`OUT-002` 指定預設上載母版為 MP4、H.264 High Profile、AAC-LC、Rec.709 SDR、固定幀率及快速啟動中繼資料；`OUT-003` 指定音訊分軌使用 48 kHz WAV，字幕來源同時包含 WebVTT 與 SRT。這些是可測試的技術交付條件，不取代創作審閱。對於每個啟用地區，必須同時檢查語言標籤、時長、響度、真峰值、字幕可剖析性、兩行限制、安全區與字幕／語音的兩個專案影格對齊要求。

### 4.2 `manifest.json` 的交付責任

交付清單應列明每項面向外部的工件、其 SHA-256、語言、輸出設定檔、時間線／剪輯指紋、來源 Gate B 覆蓋、Gate C 批准、保留類別及發布狀態。它是一份交付合約，不應以檔名或資料夾存在作為完整性的替代品。

建議的責任欄位包括：

| 清單元素 | 最少證據 |
|---|---|
| 母版與上載檔案 | `encode_hash`、渲染設定檔、幀率、解像度、音訊／字幕串流報告。 |
| 時間線 | `final.otio` 雜湊、`edit_fingerprint`、各片段的 Gate B 覆蓋與來源入／出點。 |
| 本地化 | 意圖腳本版本、地區時長預檢結果、語音／字幕雜湊、響度與真峰值。 |
| 封裝及中繼資料 | 標題、說明、章節、標籤、縮圖、授權附註及有效性報告。 |
| 風險與偏差 | `deviations.json`、未自動驗證的 Studio 步驟、例外豁免、未解決但已接受的風險。 |
| 發布 | 發布意圖、遠端 ID、遠端驗證、披露決定、Gate D 綁定之 `encode_hash`、公開收據。 |

### 4.3 批准綁定：核准意思、證據與公開位元組

v2 將批准綁定至工件雜湊，避免同一檔名的內容悄然替換。v3 進一步指出，僅依賴輸出雜湊會讓無害的重新編碼或工具鏈升級錯誤地撤銷剪輯批准。因此 `APR-001` 至 `APR-007` 分開三種身分：

| 身分 | 對應問題 | Gate A／B／C | Gate D |
|---|---|---|---|
| `edit_fingerprint` | 是否為同一組編輯決策？ | 必須綁定。 | 作為背景證據，但不足夠。 |
| `reviewed_content_hashes` | 審閱者是否看過同一素材？ | 必須綁定。 | 保留於審核鏈。 |
| `encode_hash` | 是否為同一個將被公開的檔案位元組？ | 作為渲染證據。 | 必須綁定至實際已上載檔案。 |

`edit_fingerprint` 包含規範化時間線中的鏡頭識別碼、來源工件雜湊、入點／出點、記錄位置、轉場、效果、重新構圖、音訊與字幕參照、影響交付的標記文字、渲染設定檔與封裝順序；它排除檔案絕對路徑、建立時間、編碼器版本字串、非輸出註解及其他非編輯資料。

下列延續規則應以測試固定：

- 相同 `edit_fingerprint` 與相同已審閱內容、僅重新渲染：Gate A／B／C 可延續，新增 `encode_hash` 作證據；
- 一格修剪、替換片段、改變渲染設定檔或改變封裝順序：撤銷受影響批准；
- 只修改中繼資料：畫面批准可以延續，但需要新的中繼資料批准與 Gate D；
- 修正字幕：畫面批准可以延續，但字幕內容批准必須重做；
- 綱要遷移且編輯含義未變：按 `EVO-004` 記錄 `migrated_from` 後解析延續，不可複製一份看似全新的批准。

這種細分不是為了降低審閱嚴謹度，而是讓批准正確地覆蓋人員實際審閱的對象，同時把不可逆公開動作綁緊到精確位元組。

### 4.4 稽核套件的可驗證範圍

`OPS-005` 要求稽核套件包括清單、批准、提示、決策、模型與工具版本、雜湊、成本、品質報告、披露記錄及發布收據。完整稽核還應能回答：

1. 這段公開影片由哪一個 `encode_hash`、哪一份交付清單及哪一次 Gate D 授權？
2. 這一段鏡頭由哪一個 Gate B 接受，使用哪些護照、條件資產、路由與成本？
3. 哪些外部來源只作工藝參考，哪些來源獲准包含於最終剪輯？
4. 哪個權利、同意或保留規則在何時被評估？
5. 哪些品質結果是確定性失敗、哪些是經校準的證據、哪些由人工豁免？
6. 哪些鏡頭已套用 `DEG` 步驟，而 Gate C 是否看過該偏差？
7. 上載為何可恢復、遠端狀態如何驗證，以及誰在何時授權公開？

SHA-256 譜系是強制內部要求。C2PA 是可選的外部來源資訊簽署功能，不能以缺少 C2PA 為由削弱內部工件雜湊、事件、批准與收據。反之，即使附有 C2PA，亦不能取代權利清單、同意證據或 Gate D。

---

## 5. 受防護上載、遠端驗證與公開發布

### 5.1 四個關卡的交付分工

交付及發布階段的關卡不可合併。其責任如下：

| 關卡 | 核准對象 | 主要阻擋風險 | 不授權的事 |
|---|---|---|---|
| Gate A | 動態預演、最長地區時長與結構。 | 未經核准便產生付費／遠端最終影片。 | 不授權片段選擇或公開發布。 |
| Gate B | 情境中的每段候選片段。 | 局部可用但破壞相鄰鏡頭、連續性或原創性的片段。 | 不授權最終母版或上載。 |
| Gate C | 完整母版、每個地區交付、偏差、品質、權利及稽核套件。 | 不完整、不可解碼、未披露或未審閱的交付。 | 不授權把遠端資產設為公開。 |
| Gate D | 已上載的精確 `encode_hash`、遠端 ID、元資料雜湊、披露與可見度改變。 | 把錯誤檔案、錯誤設定或未驗證遠端資產公開。 | 不重新審批創意內容；它只授權最終曝光。 |

Gate D 是公開的最後防線，故 `APR-007` 使其綁定實際上載檔案的位元組雜湊。以「剪輯大概相同」代替此條件，對不可逆公開操作而言不足夠。

### 5.2 Guarded upload 的必經步驟

受防護上載的正確順序是：

1. **寫入發布意圖。** 在任何網絡請求前，以客戶端冪等性鍵建立不可變意圖記錄（`WF-012`）。它包含交付 ID、本地 `encode_hash`、目標頻道、預期隱私狀態、metadata hash、披露決定與操作鍵。
2. **對帳舊意圖。** 若同一鍵已產生遠端影片或可續傳工作階段，恢復／採用既有資產；不得盲目再上載。
3. **使用最小權限憑證。** OAuth 憑證只由發布服務保存。審閱 UI、代理及一般工作者不應擁有可改變可見度的權限。
4. **以可續傳工作階段上載。** 持久保存 session URI（`DIS-007`），中斷時從該工作階段恢復，不創建第二段影片。
5. **預設私人或不公開。** 發布服務不可把初次上載設為 `public`。這是可逆傳輸階段，而非公開操作。
6. **套用已批准資料。** 包括標題、說明、標籤、localizations、縮圖、字幕、預設音訊語言、面向兒童設定及合成內容披露。
7. **對沒有 API 的項目產生 runbook。** 不得把待人手操作的項目標記為 API 已完成。

任何步驟失敗時，最安全的預設是保留遠端資產為 `private` 或 `unlisted`、保存收據及錯誤證據、指回擁有該問題的階段。不可把「上載傳輸已完成」誤當成「交付已驗證」。

### 5.3 Remote verification 是與平台的讀回比對

上載後，第 18 階段應讀回遠端影片記錄，至少比較：遠端影片 ID、處理狀態、隱私狀態、時長（容許一幀和平台四捨五入差異）、標題、描述、標籤、類別、預設音訊語言、縮圖存在與否、字幕軌與語言代碼、章節可否從描述重新剖析，以及 `status.containsSyntheticMedia` 的披露值。

驗證報告應同時顯示本地與遠端識別碼，避免操作員只憑標題相似就批准錯誤版本：

| 本地資料 | 遠端資料 | 結果規則 |
|---|---|---|
| `release_id`、`encode_hash`、metadata hash | video ID、可見度、讀回 metadata、處理狀態 | 任一必要欄不符，維持非公開。 |
| 字幕雜湊與地區代碼 | captions 列表與處理狀態 | 不齊全或語言錯配，返回字幕／上載所屬階段。 |
| 披露決定與理據 | `containsSyntheticMedia` 讀回值 | 不符即阻擋 Gate D。 |
| `youtube-description.md` 章節 | 平台重新讀回的說明 | 無法符合章節規則，返回 metadata 階段。 |

遠端系統可能存在處理延遲、狀態快取或 API 顯示與 Studio UI 不同的問題。規格已要求讀回驗證，但尚未證實每種平台暫態如何表現；實作需將「仍在處理」與「永久失配」分成可重試與需人員介入的失敗類別。

### 5.4 API、自動化與 YouTube Studio 的誠實邊界

以 v3 文件列明的能力矩陣為準，以下工作可透過 YouTube Data API 自動化並讀回驗證：影片上載、私隱狀態、排程、標題、說明、標籤、類別、語言本地化文字、預設語言／音訊語言、縮圖、字幕、面向兒童聲明和合成內容披露。章節依賴說明內時間戳，可由重新讀回說明間接驗證。

但下列項目沒有相同的 API 交付與驗證路徑：

| 需要項目 | 已規定做法 | 不可宣稱 |
|---|---|---|
| 每種語言的額外音訊軌 | 以桌面版 YouTube Studio 人工新增；在 `runbooks/manual-studio-steps.md` 列出步驟並由人員勾選。 | 不可稱為 API 已上載、已遠端自動驗證。 |
| 片尾畫面和資訊卡 | 提供 Studio 手動操作手冊與人工檢查清單。 | 不可將建議資料視為平台設定已完成。 |
| 平台自動配音與創作音軌衝突 | 手動檢查；需要時先移除同語言自動配音再新增創作音軌。 | 不可假定單一 API 呼叫能解決所有音訊狀態。 |

這導向一個需要在專案初期選擇的交付策略：若必須完全自動化，採用三個獨立的按語言上載檔案；若必須只有一個 URL 並提供多音軌，接受後續 Studio 人工步驟及其不可程式驗證的稽核缺口。`OUT-004` 要求使用頻道能力矩陣作出選擇，且不得為沒有 API 的操作虛構自動化證據。

### 5.5 合成內容披露與 C2PA

`DIS-001` 至 `DIS-006` 令每次上載都有明確的合成內容披露決定、作出決定的人員和理據。只要母版含有生成媒體，預設值為肯定；要使用否定值，必須有記錄在案的人員判定，說明內容不屬逼真的經修改或合成媒體。該值在上載前作確定性檢查，並在讀回遠端資料時再次核對。

C2PA 簽署仍屬可選。若啟用，必須使用目標平台識別的 C2PA 版本；依 v3 所記載，平台延續 Content Credentials 的最低版本為 2.1。未獲平台識別的簽署不可描述成平台可見的來源資訊。無論是否簽署，內部 SHA-256 譜系、audit manifest、披露理據與上載收據仍然不可省略。

### 5.6 發布後驗證與真正的可逆性界線

Gate D 後可把可見度改為公開或排程公開，然後再次讀回狀態、metadata、字幕和披露，保存規範 URL 與收據。可見度可以再調回非公開，但瀏覽、通知、索引、轉載和下載不能可靠收回。因此「公開後可回退」只適用於有限的可見度旗標，不能當作降低 Gate D 門檻的理由。

---

## 6. 可靠性、重試、復原與故障分類

### 6.1 先分類，才決定重試

可靠系統不是把所有錯誤放入同一個 retry loop。`REL-001` 至 `REL-003` 要求每個失敗有類別、擁有人、證據與指定復原路徑。建議採用以下分類：

| 類別 | 例子 | 是否自動重試 | 復原行動 |
|---|---|---|---|
| 暫時性基礎設施 | DNS、網絡逾時、短暫 5xx、供應商短暫故障。 | 是；有界指數退避加 jitter。 | 使用同一 `operation_key` 重試並先核對意圖／已存在結果。 |
| 容量 | GPU 記憶體不足、佇列飽和、磁碟暫不足。 | 不直接重試同一路徑。 | 選用已批准的低資源路徑、等待容量或轉人工。 |
| 確定性輸入 | 無效 schema、損壞媒體、不支援容器、非法狀態轉換。 | 否。 | `BLOCKED`，指出欄位、需求 ID、來源與修正人。 |
| 品質 | `FACE_DRIFT`、`MOTION_UNNATURAL`、`DURATION_MISMATCH`。 | 依鏡頭品質重試配額。 | 最小擁有範圍重拍、變更條件或路由；消耗鏡頭預算。 |
| 分類帳矛盾 | 未滿足 `requires`、非法改變不變屬性。 | 否。 | 生成前封鎖，透過 `ADJUST_LEDGER`、`REORDER` 或敘事修訂解決。 |
| 法律／同意 | `ORIGINALITY_CEILING`、`LIKENESS_RISK`、`CONSENT_MISSING`。 | 否。 | 升級人工處理；不可自動豁免。 |
| 政策／預算 | 權利過期、私隱不符、Gate A 前遠端生成、止損。 | 否。 | 保持 `BLOCKED` 或 `P_HALTED`，等待有效證據／範圍變更。 |
| 並行 | 過時 fencing token、輸入版本在執行中改變。 | 不可盲目提交。 | 拒絕提交、保留孤立候選、產生影響報告並重新排程。 |
| 人工拒絕 | 節奏、構圖、發音或敘事目的問題。 | 不適用。 | 寫入類型化指令與拒絕代碼，只使相依後代失效。 |
| 發布驗證 | 遠端處理、字幕、metadata、披露或可見度不符。 | 可針對暫態讀回重試。 | 保持私有／不公開，修正擁有階段後再驗證。 |

暫時性重試和品質重試必須分開計帳：前者不應偷偷花掉品質候選額度，後者必須計入鏡頭封套及止損。預設可採三次有上限的暫時性指數退避，而品質重試預設最多四次；兩者都是規格起點，可由專案政策調整，不能被理解成已證實所有供應商均適用。

### 6.2 冪等性、操作鍵與外部副作用

同一邏輯操作重試時，系統必須返回既有有效工件，而非重複生成或重複上載。v3 的操作鍵由階段、排序後輸入雜湊、設定雜湊、適配器 ID、適配器版本及 `attempt_class` 組成：

```text
operation_key = sha256(
  stage || sorted(input_hashes) || config_hash ||
  adapter_id || adapter_version || attempt_class
)
```

`attempt_class` 尤其重要：技術重試應與「刻意要求一個新候選」區分。若沒有它，系統要麼把正當新候選錯誤地去重，要麼把恢復操作錯誤地再收費。

對外副作用要在請求前寫入意圖，並在重試前以該鍵核對（`WF-012`）。這個規則同時適用於供應商生成、付款／計費接受及 YouTube 上載。它是「重複請求不會重複公開」的必要機制；只有測試結果而沒有意圖記錄與對帳機制，不能證明冪等。

### 6.3 工作租約、圍欄與提交時重驗

多工作者環境中，工作者崩潰、遲到回來或同時讀到舊資料是常態。`CON-001` 至 `CON-005` 規定：

- 工作由有期限、持有人與單調遞增 `fencing_token` 的租約認領；
- 工作者以心跳續租，過期後可被另一工作者重新認領；
- 低於最新已接受權杖的寫入必須被拒絕，防止已「復活」的舊工作者覆寫新結果；
- 工作開始時記錄護照、分類帳、約束與校準等輸入版本，提交時重新驗證；
- 可變投影以樂觀併發控制寫入，衝突後讀取最新狀態而非盲目合併。

例如，鏡頭正在以 `passport:v3` 生成時，設計師把護照升至 `v4`。舊工作者可以把已產生檔案保存為具完整譜系的孤立工件，但不可提交為符合 `v4` 的候選。系統要產生影響報告，讓操作者決定是否重生成、是否審查孤立結果，或是否恢復舊護照。這比靜默接納過時結果成本低，也更可稽核。

### 6.4 相依性失效與精準修復

工件圖以 `derives`、`conditions`、`constrains`、`times`、`describes`、`measures` 和 `contains` 邊表達依賴。變更分類為 `CONTENT`、`TIMING`、`CONSTRAINT`、`METADATA`、`POLICY`、`METRIC` 或 `IDENTITY`，並由傳播矩陣計算每個後代為 `INVALID`、`REVIEW` 或 `INTACT`。

應牢記兩條營運規則：

- `INVALID` 代表內容或其依據已不可信，會以 `CONTENT` 繼續向下傳播；覆蓋它的批准要撤銷；
- `REVIEW` 只表示需要確認，不會向下傳播。若人工確認後實際改變內容，該改變會另作新事件傳播。

故此，改變鏡頭時長會使時間線、語音對齊、字幕、章節、封裝、母版與發布批准失效；改變校準檔案則使品質報告失效，不需重新生成媒體；只改 metadata 可保留畫面 Gate C，但需重新核准 metadata 與 Gate D。每次傳播前須建立不可變影響報告（`GRA-006`），不可讓工作者以臨時判斷直接修復。

---

## 7. 降級不是失敗掩飾：可交付的偏差管理

生成系統必定遇到某些鏡頭在成本、時長、品質或供應商能力限制內無法達標。若流程只有「不斷重試」與「永久停住」兩種狀態，最後往往以未記錄的人手捷徑結束。`DEG-001` 至 `DEG-004` 要求專案預先定義有序降級階梯，並把每一個實際採用的步驟記為明示偏差，於 Gate C 展示。

一個可用的階梯為：

| 層級 | 動作 | 最低批准 | 交付記錄 |
|---|---|---|---|
| `L0` | 原設計的完整動態生成。 | 無。 | 基線。 |
| `L1` | 降低動作複雜度、縮短時長或簡化鏡頭運動。 | 預算內自動。 | 偏差附註。 |
| `L2` | 嘗試替代適配器或替代條件資產。 | 預算內自動。 | 偏差附註。 |
| `L3` | 用已批准風格影格製作慢速移動、視差或受控動畫。 | 人工指令。 | 具名偏差。 |
| `L4` | 以同一節拍的已批准替代覆蓋素材取代。 | 人工指令。 | 具名偏差。 |
| `L5` | 刪除鏡頭並重新調整相鄰時長。 | 人工指令加敘事審核。 | 具名偏差與敘事理據。 |
| `L6` | 重新設計、刪剪場景或以製作決定接受已界定風險。 | 人工製作負責人。 | 具名偏差與完整理據。 |

`L5` 特別需要敘事審核，確認鏡頭的 `narrative_purpose` 已由其他鏡頭承擔，或被有意放棄。降級後不可把品質報告改寫成「完全通過」；應在 `deviations.json` 記錄原始意圖、觸發原因、所用層級、批准人、影響範圍、替代資產及殘留風險。這令 Gate C 所看到的是實際發布版本，而不是理想但未達成的計劃。

---

## 8. Windows 可攜性與綱要演進

### 8.1 Windows 是部署條件，不是註腳

初始部署目標為 Windows。內容定址儲存、CJK 專案標題、深層交付目錄與跨平台工具鏈，會暴露出路徑長度、保留名稱、大小寫、編碼和 shell 解析差異。`PLT-001` 至 `PLT-005` 的要求如下：

| 關注 | 必須實施的規則 | 驗證例子 |
|---|---|---|
| 路徑長度 | 工件根目錄可設定為短絕對路徑；檔案 API 支援延伸長度路徑。 | 長 `project_id` 加深層 `delivery`／`audit` 路徑仍能建立、讀取及刪除。 |
| 檔名 | 只以工件 ID 與小寫十六進制雜湊衍生；不用使用者標題。 | `香港：月門/CON` 等輸入標題不能形成路徑。 |
| 保留名稱與大小寫 | 避開 `CON`、`PRN`、`AUX` 等名稱；雜湊一律小寫。 | 在大小寫不敏感磁碟不會把不同工件混淆。 |
| UTF-8 與字幕 | 所有文字工件為 UTF-8；WebVTT 有 `WEBVTT` 標頭；SRT 行尾與最終換行以剖析器測試。 | 粵語繁體字幕、簡體字幕、英文混合標點可被目標播放器剖析。 |
| 子程序 | 以 argument array 呼叫 FFmpeg、下載器與其他工具；禁止 shell 插值。 | 空格、引號、`&`、`$`、CJK 路徑及惡意檔名不改變命令語義。 |

此等規則也保護工件雜湊。若 Git checkout、編輯器或平台默默改變行結束符，文字工件雜湊與批准證據都會失真。儲存庫和產物格式應明確固定行尾與編碼慣例，並在部署目標系統實測，而不是只在開發者的 macOS 或 Linux 機器通過。

### 8.2 綱要演進必須建立新工件

v2 已有 `schema_version`，但缺少演進政策。`EVO-001` 至 `EVO-004` 補上四項規則：

1. 採語義版本：次要版本只新增可選欄位；主要版本才可改變／移除必要欄位；
2. 讀取器須保留未知可選欄位，但拒絕未實作的主要版本；
3. 遷移建立新不可變工件，並記錄 `migrated_from`；絕不原地改寫舊工件；
4. 遷移後的批准按 `APR-003` 延續規則解析，不得靜默複製。

一個遷移器的輸出可以概念化為：

```json
{
  "schema": "video-flow/migration-record",
  "schema_version": "3.0.0",
  "migration_id": "mig_01J...",
  "source_artifact_id": "art_v2_01J...",
  "target_artifact_id": "art_v3_01J...",
  "migrated_from": "sha256:...",
  "source_schema_version": "2.0.0",
  "target_schema_version": "3.0.0",
  "semantic_change": false,
  "edit_fingerprint_before": "sha256:...",
  "edit_fingerprint_after": "sha256:...",
  "approval_resolution": "carried-forward-with-evidence"
}
```

若遷移改變了鏡頭時長、時間線語義、內容雜湊或批准涵蓋的素材，便不是單純結構遷移；必須以正常失效規則撤銷／過時化批准。若 `edit_fingerprint` 與審閱內容不變，則可連同可追溯遷移鏈延續，並新增工件雜湊作證據。

---

## 9. 可觀測性、營運者操作手冊與指標

### 9.1 健康投影不是原始日誌

`OBS-001` 要求每個專案暴露健康狀態投影。原始 JSONL 事件與大量工作者日誌對排障有用，但不能取代操作員的即時問題視圖。健康投影至少應顯示：

- 當前專案階段與 Gate A–D 的就緒度／覆蓋率；
- `BLOCKED`、`DEGRADED`、`CUT` 鏡頭及其擁有人、原因碼、最近事件；
- 按嚴重程度的未解決品質、權利、披露與平台發現；
- 專案及鏡頭封套的 `escrowed`、`committed`、`reconciled`，以及離止損和硬上限的距離；
- 過期、撤銷或 `stale` 的批准；
- 最舊未解決人工請求的年齡、所屬角色與 SLA；
- 租約、心跳、停滯工作與可恢復／不可恢復錯誤；
- 保留期即將到期與已逾期的資產數目。

任何計量資料均應使用結構化欄位，按 `project_id`、`shot_id`、`stage`、`adapter_id`、`operation_key`、`requirement_id`、`severity`、`failure_class` 和 `rate_card_version` 關聯，並在匯出／展示前套用已測試的遮蔽規則（`OBS-003`）。

### 9.2 停滯偵測與一對一操作員動作

監測若只能告警而沒有可執行處置，只會把不確定性轉交給值班人員。`OBS-002`、`OBS-004` 要求每個停滯狀況對應已聲明操作：

| 偵測訊號 | 判定 | 操作員 runbook |
|---|---|---|
| 租約過期且沒有心跳 | 工作者可能終止或失聯。 | 以更高 `fencing_token` 收回；檢查操作鍵與供應商意圖，再決定恢復或核對。 |
| 鏡頭在單一狀態超過閾值 | 可能排隊、供應商卡住或等待人員。 | 檢查最後操作、租約、錯誤分類與人工隊列；勿直接重派付費工作。 |
| Gate 已就緒但未審核 | 人工瓶頸。 | 通知指定審閱角色，顯示範圍、風險、成本與最舊請求年齡。 |
| 有託管額度但無活動租約 | 可能 escrow leak。 | 核對供應商意圖與收據；確認無未完成請求後釋放並記錄更正。 |
| 品質重試已達上限且分數未改善 | 生成迴圈無效。 | 停止重試，顯示 `DEG` 階梯與負責製作人。 |
| `stale` 批准累積 | 變更影響未被消化。 | 批量呈示低成本確認，但不可自動把 `stale` 改回有效。 |
| 保留期逾期 | 私隱／成本風險。 | 執行刪除或隔離，保存刪除事件與保留理由。 |

runbook 必須說明何時禁止操作員「按重試」、何時可恢復、何時需要新 Gate、何時需要權利或法務負責人。它亦應指向影響報告與工件雜湊，而不是只指向一條錯誤訊息。

### 9.3 營運指標：衡量管治是否減少浪費

下表將 v2／v3 的指標整理成可行的營運問題：

| 指標 | 問題 | 警戒解讀 |
|---|---|---|
| Gate A 前遠端生成率 | 是否真的在成本前核准結構？ | 任何非零都可能是政策繞過，目標為零。 |
| 每獲接納秒數的生成秒數／成本 | 候選數與重試是否失控？ | 上升不必然代表差，但應配合品質與優先度分析。 |
| 每鏡頭人工介入與拒絕原因分布 | 哪些流程／適配器造成返工？ | 重複原因應促成已提升限制提案，而不是堆積自由文字。 |
| 生成前分類帳矛盾／生成後連戲發現比例 | 是否把可避免錯誤前移？ | 長期過低可能表示分類帳沒有表達真正狀態。 |
| 封套止損觸發與 `DEG` 層級分布 | 哪些鏡頭類型無法按既定成本完成？ | `L3` 以上常用時，需重估能力與腳本設計。 |
| 託管準確度 | 託管、承諾與收據是否相符？ | 持續差異表示費率卡或收據整合失真。 |
| 恢復成功率與重複外部副作用 | 中斷後是否安全恢復？ | 重複上載／可計費請求屬重大事故。 |
| 語言地區調整與改寫請求 | 最長語言預檢是否足夠？ | 高比例溢出表示草稿語音、餘裕或劇本流程需修訂。 |
| 發布驗證失敗與非預期公開數 | Guarded release 是否可信？ | 非預期公開、未披露合成發佈、權利關卡繞過、秘密洩漏、核准繞過和預算超支目標均為零。 |

指標不能代替創意審閱。它們的作用是指出系統在何處違反自己的承諾，讓營運者選擇最小而可稽核的修復。

---

## 10. 實作路線圖、測試策略與發行關卡

### 10.1 里程碑應以可驗證垂直切片交付

以下路線圖採 v3 的七個里程碑。後續里程碑不應被前置「假完成」掩蓋；尤其不可先接入昂貴模型，再回頭補做狀態、圖、審批和預算控制。

| 里程碑 | 重點交付 | 最小退出證據 | 尚不可宣稱 |
|---|---|---|---|
| M0 合約、圖與控制平面 | JSON Schemas、資料庫、雙層狀態機、工件圖、影響報告、租約、剪輯指紋、內容定址儲存。 | 非法狀態與過時批准確定性失敗；停止後不產生重複工件；圖夾具傳播符合矩陣。 | 不代表可生成或發布影片。 |
| M1 參考分析切片 | 權利閘門、擷取／標準化、片段候選審核、保留清理、工藝／受保護表達分區、原創性基線。 | 至少五個多樣且獲授權／合成參考資料得到審閱者批准片段或有效「無匹配」。 | 不代表有自動權利清權或可公開重用來源。 |
| M2 聖經與分類帳 | 護照編輯、屬性分類、分類帳求解、矛盾報告、版本與影響。 | 植入的未滿足前置條件、未宣告變更、非法不變項效果均被偵測；100 鏡頭求解遠低於一秒。 | 不代表感知連戲已校準。 |
| M3 故事板、地區預檢與 Gate A | 線框圖、結構化評析、意圖劇本、草稿語音時長、OTIO 動態預演、類型化指令與 Gate A。 | 三場景、至少八鏡頭先導在未付費生成下通過 Gate A；每個節拍容納三地區。 | 不代表最終 TTS 時長完全不漂移。 |
| M4 預算化生成與 Gate B | 適配器登記冊、本機／遠端路線、封套／託管／止損、費率卡、媒體 QC、原創性／肖像篩查、情境化 Gate B。 | 強制超支在准入時拒絕；Gate A 前無遠端請求；原創性超標封鎖並升級。 | 不代表語義指標已在所有專案校準。 |
| M5 編輯、本地化、交付與 Gate C | 確定性渲染、混音、字幕、封裝、偏差、QC 報告、audit export、Gate C。 | 三地區交付可解碼同步；未變剪輯可延續批准；一格變更撤銷批准。 | 不代表任何平台已接收或公開。 |
| M6 受防護發布與 Gate D | 最小權限 OAuth、意圖／可續傳上載、metadata／字幕／縮圖、披露、遠端驗證、Studio runbook、Gate D、發佈後驗證。 | 重試不建立第二影片；未記錄披露時拒絕上載；失配保持非公開；Gate D 綁定上載位元組。 | 不代表 Studio 手動功能能自動驗證。 |

### 10.2 測試策略：從合約到非公開端對端演練

測試固定裝置應採合成或明確授權媒體，避免把第三方內容依賴帶入 CI。以下測試族群必須各自存在，因為端對端通過不能取代對邊界條件的精確證明：

| 測試類型 | 驗證主題 |
|---|---|
| 綱要與合約 | 必填／可選欄位、未知可選欄位保留、未實作主要版本拒絕、所有需求 ID 可追溯。 |
| 狀態與關卡 | 專案／鏡頭允許與禁止轉移、Gate 覆蓋失去、撤銷、到期、`BLOCKED`／`DEGRADED`／`CUT` 回復。 |
| 工件圖 | 傳播矩陣逐格、`REVIEW` 不向下傳播、深鏈終止、批准撤銷與過時標示、影響報告不可變。 |
| 指紋與渲染 | 相同剪輯重渲延續、一格修剪失效、設定檔改變失效、metadata／字幕的不同覆蓋、遷移延續。 |
| 並行與冪等 | 租約收回、過時權杖拒絕、飛行中輸入改變提交失敗、並行宣告只產生一筆可計費請求。 |
| 分類帳 | 前置條件、未宣告變更、不變項、重新排序／刪鏡後重解、預期狀態注入品質評析。 |
| 預算與收據 | 封套邊界、最壞情況失敗費、崩潰時釋放託管、止損、費率卡版本、對帳容差。 |
| 媒體與本地化 | 時基、字幕、WebVTT／SRT、響度、真峰值、語言地區時長階梯、輸出 profile。 |
| 原創性與安全 | 近似重複、標誌／螢幕文字、組裝序列相似、惡意 metadata／字幕／轉錄提示注入、超大媒體、秘密金絲雀。 |
| 平台與發布 | Windows 路徑、Unicode、大小寫、保留名稱；上載前披露；重試不重複上載；失配不公開；Gate D 位元組綁定。 |
| 端對端 | 假遠端適配器至 Gate C；非公開測試頻道至 Gate D；每階段中斷後可恢復。 |

### 10.3 發行關卡

發布候選版本只有在下列條件同時成立時才可接受：

- 每個需求 ID 有至少一項自動測試或已記錄的人工驗證；
- 沒有未解決的嚴重／重大確定性媒體故障；
- 批准、預算、披露及發布繞過均為失敗關閉；
- 先導項目可在每個階段中斷後恢復；
- audit bundle 驗證所有雜湊，且金絲雀秘密沒有出現；
- 收據與對帳在既定容差內相符；
- 未變更剪輯重渲可延續批准，而一格變更會撤銷；
- Markdown、JSON、交叉引用及必要的工作流程資產連結均可剖析。

這些是**產品／系統發行**關卡；它們不同於某一影片的 Gate C／D。前者問「平台實作是否可靠」，後者問「這一個交付與這一次公開是否被正確批准」。

---

## 11. 由 v1／v2 遷移至 v3

### 11.1 遷移原則

遷移不是把 JSON 的 `schema_version` 改成 `3.0.0`。v1 的資料多為創意工作流程與固定閾值；v2 有不可變工件、專案狀態及雜湊批准；v3 增加了鏡頭生命週期、圖邊、變更分類、租約、預算帳本、連續性分類帳、類型化指令、披露與 Windows／演進要求。任何自動遷移都必須建立新工件、保留來源、產出影響報告，並誠實標記無法補回的歷史證據。

### 11.2 v1 至 v2：先把計劃轉為可驗證合約

v1 專案通常需要：

1. 把故事線、場景、鏡頭轉為有效且版本化的 JSON，修正示例式註解與含糊欄位；
2. 為每個實體建立穩定 ID，並補上權利依據、保留類別和來源雜湊；
3. 把 Remotion 作為渲染器／審閱工具，而非唯一編輯真相；建立 `OpenTimelineIO`；
4. 把供應商模型名稱移至能力適配器登記冊，保留鏡頭意圖為供應商中立合約；
5. 把 v1 固定閾值（例如 `0.72`、`0.78`）降格為待校準的實驗起點，不能直接當生產阻擋條件；
6. 重建批准為包含範圍、工件雜湊、審批人、時間、決定、評論與撤銷／到期的記錄；
7. 將最終批准拆分為 Gate C 的交付批准與 Gate D 的公開授權。

v1 沒有定義可靠的自動 v1→v2 遷移，因此任何歷史人手批准、成本與來源資料若未曾結構化記錄，應匯入為人工認證的歷史證據，並標記完整度，而不可虛構精確 `artifact_hash` 或時間戳。

### 11.3 v2 至 v3：補上執行模型，而非只加欄位

v2 專案應按以下工作包遷移：

| v2 資產／機制 | v3 所需補充 | 遷移注意 |
|---|---|---|
| 全域專案狀態 | 專案階段加每鏡頭生命週期（`STA-*`）。 | 不可從單一 `MASTER_REVIEW` 可靠推斷每一鏡頭曾否 Gate B；缺少證據時標記待重審。 |
| `continuity_in/out` 版本標記 | `story_time`、`requires`、`effects`、護照不變／有狀態分類及分類帳。 | 需要人員／敘事審閱補寫實際狀態轉移，不能自動從嵌入分數推論。 |
| 無類型 `input_artifact_ids` | 具 `derives`／`conditions` 等類型的圖邊和變更矩陣。 | 無法確定的舊依賴應標為未知並限制自動失效範圍。 |
| 雜湊綁定批准 | `edit_fingerprint`、審閱內容雜湊、審閱渲染雜湊及延續規則。 | 舊批准未有足夠審閱證據時，不可自動升格為 v3 Gate C／D。 |
| 全域預算與儲備 | 封套、託管、承諾、對帳、止損和費率卡。 | 歷史成本可匯入為 `reconciled`，但不可倒推成已執行的准入控制。 |
| 自由文字回饋 | `DIR-*` 封閉指令、理由與拒絕碼。 | 過去評論可存檔；未能可靠分類的項目不可自動執行。 |
| 畫面鎖定後本地化 | Gate A 前意圖劇本與地區時長預檢。 | 現有已鎖畫面需重新量度；溢出要以變更／重審處理。 |
| 一般上載流程 | 發布意圖、可續傳 session URI、披露、遠端驗證、Gate D 位元組綁定。 | 既有已公開影片可建立歷史收據，但無法事後證明當初防護程序已執行。 |

遷移完成的最低定義不是「所有資料能被 v3 讀取」，而是：每個新 v3 工件有 `migrated_from`；每個批准有明確延續、過時或撤銷結果；無法補回的執行證據被列為風險；新工作一律使用 v3 操作鍵、租約、預算與 Gate 規則。

---

## 12. 假設、風險、未解決問題與誠實限制

### 12.1 需要由專案確認的假設

| 假設 | 若不成立的後果 | 應採取的確認 |
|---|---|---|
| 每個專案鎖定幀率、畫面比例與色彩設定檔。 | 時間線、字幕、時長與母版比較變得含糊。 | 在 `project.json` 驗證；多輸出設定檔使用不同時間線版本。 |
| 使用者提供或批准所有最終故事內容。 | 代理可能創作未批准對白或敘事。 | 以意圖劇本、類型化指令與 Gate A 保持邊界。 |
| 參考資料主要用於鏡頭工藝，而非最終重用。 | 權利與原創性風險提高。 | 要求明確來源許可；分區工藝與受保護表達。 |
| 人員可拒絕任何自動建議。 | 分數會被錯當成創意裁決。 | UI 不把任何語義分數當成自動批准。 |
| 主要渠道為 YouTube。 | 其他平台的披露、音軌、metadata 與驗證能力可能不同。 | 把渠道行為隔離在發布適配器與能力矩陣。 |
| Windows 是初始部署目標。 | 未測路徑與編碼問題會在現場出現。 | 在 Windows CI／實機執行 `PLT-*` 固定裝置。 |

### 12.2 已記錄但尚未解決的議題

1. **原創性上限校準**：沒有原則性的通用閾值。建立足夠的人工標註「太接近／可接受」配對成本高，未校準前應保守地作為人工發現，而不是武斷自動通過。
2. **分類帳表達能力**：離散 `requires`／`effects` 很適合物件持有者、服裝、揭示與地點狀態，卻不善表達疲勞、日照、天氣、傷勢程度等連續量。加入範圍會提高作者負擔與求解複雜度。
3. **草稿與最終聲音時長漂移**：Gate A 量度的是草稿語音。最終供應商聲音、表演和語速可能超出餘裕；須按聲音與語言量度可接受漂移。
4. **適配器聲明誠實性**：時長量化、成本、取消、退款、保留和能力均可能由供應商改變。登記冊要定期以實證測試重驗，不能只信文件。
5. **人工 Studio 步驟的稽核缺口**：額外音軌、片尾畫面及資訊卡等沒有對等 API 路徑。人工核對清單只能部分降低風險，不能轉變成遠端自動驗證。
6. **提升限制的相互作用**：重複拒絕可產生有用約束，但約束累積可能互相矛盾或令提示過長、品質下降。上限可控制增長，未能自動理解語義衝突。
7. **跨語言唇形同步**：旁白與非特寫較容易；同一已鎖畫面上的英語、普通話、粵語特寫對白仍有真實可行性限制。須先以目標鏡頭大小與聲音作試點。
8. **確定性渲染邊界**：固定編碼器、旗標與中繼資料可提高可重現性，但跨主要編碼器版本的位元完全一致未有保證。`APR-006` 的差異允許清單是必要後備，不是保證。
9. **C2PA 的平台可見性**：可選簽署須跟隨平台認可版本；平台支援與顯示行為會演變，不能以舊測試永久證明。

### 12.3 不屬於本系統承諾的能力

Video Flow 不自動清除版權，不提供法律意見，不繞過存取控制，不進行未授權聲音／肖像複製，不對私人個人做開放集識別，不無人監督改寫已批准故事，不承諾即時生成或即時協作，也不保證機率生成模型的輸出確定性。它所追求的是**確定性組裝、可追溯決策及受控失敗**，不是把不確定生成偽裝成已解決的工程問題。

---

## 13. 最終評估

Video Flow 的成熟度演進可簡化為：v1 說明應製作甚麼；v2 說明一個可持續的製作系統要保存甚麼；v3 說明該系統在變更、並行、成本壓力與公開風險下如何不失控。v3 的優點不是加入更多代理或更多模型名稱，而是把原本只能靠操作習慣維持的安全性改寫成可檢查的機制：Gate A 前的遠端生成不可准入、准入前必須託管最壞情況成本、過時工作者不可提交、批准不能被檔名偷換、上載不能直接公開、披露不能遺漏，且沒有 API 的平台限制不能被假裝為自動化。

代價亦清楚：控制平面比單純生成管線複雜得多，需要資料庫、圖遍歷、審閱 UI、權利輸入、費率卡、收據整合、Windows 測試、操作手冊和人員角色。若這些元件只是文件而非已測實作，系統仍是**高品質設計基準**，不是已證明可投產的產品。

因此，最誠實的結論是：v3 提供了可建立受管治影片交付系統的充分藍圖，但尚未提供已完成的實作證據。應先交付 M0 的控制基礎、M1／M2 的本地與符號驗證、M3 的三語 Gate A 試點，才接入任何昂貴遠端生成；之後以受控測試頻道驗證 M6。只有當工件、收據、批准、披露、遠端讀回與復原演練都能留下可獨立檢查的證據時，「可發布」才由規格承諾變成營運事實。

---

## 附錄 A：要求家族參考

下表方便把營運行為追溯回規範要求；它不是要求全文的替代品。

| 家族 | 主題 | 本卷中的運用 |
|---|---|---|
| `IN` | 專案、鏡頭、`story_time`、對白節拍和輸入驗證。 | 預算、分類帳、本地化和輸出配置的前提。 |
| `REF` | 參考資料權利、片段、保留、原創性基線與無匹配結果。 | 權利／私隱與原創性篩查。 |
| `ANA` | 分析觀察、推論／未知及工藝／表達分區。 | 防止將受保護表達帶入生成提示。 |
| `CRE` | 視覺聖經、護照、版本與狀態屬性。 | 連續性、肖像與條件資產譜系。 |
| `STA` | 專案階段與鏡頭生命週期。 | Gate 覆蓋、阻塞、降級與回退。 |
| `WF` | 冪等、恢復、角色、關卡和外部副作用意圖。 | 操作鍵、上載意圖、發布安全。 |
| `GRA` | 有類型工件圖、變更類別、失效與影響報告。 | 精準修復、批准撤銷與過時處理。 |
| `APR` | `edit_fingerprint`、內容／渲染／編碼證據與延續。 | Gate A–D 及遷移批准語義。 |
| `CON` | 租約、心跳、圍欄與提交重驗。 | 多工作者安全和單次計費。 |
| `LED` | 符號化連續性分類帳。 | 生成前阻擋矛盾、生成後提供預期狀態。 |
| `ORG` | 原創性上限與受同意肖像篩查。 | 權利相關品質風險的人工升級。 |
| `DIR` | 類型化人員指令、拒絕碼與提升約束。 | runbook、返工與偏差的可操作化。 |
| `QUA` | 確定性檢查、校準語義指標與結構化評析。 | Gate 前品質證據分層。 |
| `BUD` | 封套、託管、准入、止損、費率卡與報告。 | 成本管治與降級觸發。 |
| `LOC` | 三語地區、時長預檢、字幕與響度。 | 交付套件完整性與 Gate A 前可行性。 |
| `PKG` | 封裝、章節、縮圖、metadata。 | 上載前驗證與遠端讀回。 |
| `OUT` | OTIO、上載編碼、分軌、時長對帳與頻道能力。 | 可交付母版與 API／Studio 分界。 |
| `DIS` | 合成媒體披露、C2PA 與可續傳上載。 | Guarded upload 與 Gate D。 |
| `RGT` | 權利、同意、地域、渠道、到期與保留。 | 上載前及發布時的政策執行。 |
| `REL` | 故障類別與重試行為。 | 復原而非盲目重試。 |
| `DEG` | 降級階梯與偏差記錄。 | 止損後仍可誠實交付。 |
| `PLT` | Windows 路徑、檔名、UTF-8、子程序與平台測試。 | 部署可攜性與安全。 |
| `EVO` | 語義版本、未知欄位、不可變遷移與批准解析。 | v1／v2 到 v3 的可信遷移。 |
| `OBS` | 健康投影、停滯、遮蔽與操作員動作。 | 值班、告警與 runbook。 |
| `OPS` | 工件沿革、成本、秘密、不受信任內容與 audit。 | 全程可追溯與安全。 |

## 附錄 B：實際採用檢查清單

### B.1 啟動前：不可跳過的管治基礎

- [ ] 已選定 v3 作為新工作之規範基準，並凍結適用的要求版本。
- [ ] 已建立短路徑的工件根目錄，並在 Windows 驗證延伸路徑、Unicode、保留名稱及大小寫案例。
- [ ] 已有不可變工件封套、SHA-256、僅追加事件、操作鍵與資料庫備份／復原策略。
- [ ] 已實作雙層狀態機、Gate 覆蓋和禁止轉移的失敗關閉測試。
- [ ] 已實作圖邊、變更分類、影響報告、批准撤銷／過時規則。
- [ ] 已實作租約、心跳、圍欄權杖與提交時輸入版本重驗。
- [ ] 已建立秘密儲存與遮蔽金絲雀測試；OAuth／Cookie 不會進入日誌、提示或 audit。

### B.2 專案接收：未花費前先證明可做

- [ ] `project.json` 含輸出設定檔、三語地區、保留、預算、響度、披露與渲染政策。
- [ ] 所有 `shot_id`、實體 ID、`story_time`、對白節拍與相依關係通過驗證。
- [ ] 每項參考、音樂、字型、標誌、肖像及聲音有權利／同意記錄與到期控制。
- [ ] 私隱資料分類與供應商限制已完成；遠端可用性不是預設。
- [ ] 費率卡來自已對帳收據與本機基準；未知成本未偽裝為估算。
- [ ] 已分配交付儲備與鏡頭封套，並設定止損與降級階梯。

### B.3 生成前：先驗證結構、連續性與語言

- [ ] 視覺聖經已鎖定；護照區分不變與有狀態屬性。
- [ ] 分類帳求解乾淨；每個矛盾有指向鏡頭、變數與修正負責人的報告。
- [ ] 每個參考分析已分開可轉移工藝與受保護表達，並保存原創性基線。
- [ ] 每個對白節拍已在英語、普通話及粵語量度草稿語音時長。
- [ ] 動態預演採用最長地區時長及餘裕；Gate A 批准綁定正確指紋與證據。
- [ ] 政策和預算引擎實證阻擋了 Gate A 前的遠端最終影片生成。

### B.4 生成與審閱：讓成本和返工有界

- [ ] 每個適配器具版本化能力、時長量化、隱私、保留、成本與取消聲明。
- [ ] 每項付費工作先通過最壞情況准入並成功託管。
- [ ] 暫時性重試與品質重試分開計數和計費。
- [ ] 確定性媒體檢查在語義／美學評析前運行。
- [ ] 感知連續性收到分類帳預期狀態；原創性和肖像發現獨立呈示。
- [ ] 人員回饋以 `ACCEPT`、`TRIM`、`RESHOOT`、`DEGRADE` 等類型化指令記錄。
- [ ] Gate B 在前後鏡頭脈絡中覆蓋每個非 `CUT` 鏡頭；批准範圍可查。
- [ ] 止損觸發後停止無效重試，改為階梯與人工決定。

### B.5 交付與 Gate C：交付的是證據完整的套件

- [ ] `final.otio`、`edit_fingerprint`、母版、上載版本、三語音訊、VTT／SRT、圖像及 metadata 都在交付清單中。
- [ ] 所有母版可解碼至尾、符合 profile、字幕對齊、響度與真峰值合格。
- [ ] 章節、標籤長度、縮圖與封裝順序通過驗證。
- [ ] 每個參考關聯鏡頭與組裝母版都完成原創性篩查；發現有人工決定。
- [ ] `deviations.json` 已列出所有降級與殘留風險。
- [ ] audit bundle 可驗證雜湊，並包含權利、批准、提示、工具／模型、成本、品質、披露與收據。
- [ ] Gate C 已審閱實際交付，不是舊預覽或可變檔名。

### B.6 上載、Gate D 與公開：先非公開，後授權

- [ ] 上載前已有發布意圖及冪等性鍵；重試會查找既有遠端資產／session URI。
- [ ] OAuth 權限最小化；初次可見度為 `private` 或 `unlisted`。
- [ ] 合成內容披露決定、作者與理據已記錄，並在上載前驗證。
- [ ] metadata、localizations、字幕、縮圖、兒童設定和披露按已批准清單套用。
- [ ] Remote verification 已讀回時長、處理、隱私、metadata、字幕、縮圖、章節與披露；任何失配保持非公開。
- [ ] 額外音軌、片尾畫面／資訊卡等無 API 工作已有 Studio runbook 和人工勾選；未標示為自動驗證。
- [ ] Gate D 綁定精確遠端 ID、上載 `encode_hash`、metadata hash、披露狀態與可見度改變。
- [ ] 公開後已讀回驗證並保存 URL／收據；回退 runbook 可用且明示其無法收回的後果。

### B.7 持續營運：每次發布後都讓系統更誠實

- [ ] 健康投影顯示 Gate、阻塞、降級、未解決發現、託管、過時批准與人工隊列。
- [ ] 每種停滯情況有指定操作員行動，而非只產生告警。
- [ ] 以收據和基準持續更新費率卡，且更新會版本化。
- [ ] 以標註資料重新校準語義與原創性指標；校準變更只使報告失效，不會靜默重寫媒體判定。
- [ ] 定期演練工作者中斷、租約收回、託管洩漏、遠端驗證失敗及非公開回退。
- [ ] 平台能力矩陣、披露欄位與 C2PA 相容版本按排程重新驗證。
- [ ] 對 v1／v2 歷史資產，保留遷移鏈與證據缺口；不把新控制倒灌成虛假的歷史事實。
