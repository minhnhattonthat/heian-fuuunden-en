# Glossary - Heian Fuuunden

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` enforces the tables below (a JP term in the line needs its EN form) and the Avoid column.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Seimei-sama, Hiroyuki-dono). 殿 -> -dono, 様 -> -sama (after a name or title), 姫 -> -hime
  after a name, otherwise "Princess". Name order: Western (given name first); historical "no" names keep their form
  (Taira no Masakado, Abe no Seimei). The check fails a line with 〜殿/〜様 and no -dono/-sama.
- Romanisation source: no official English exists and no earlier patch (docs/re/prior-work.md): Hepburn without
  macrons (Kumano Hongu, Ise Saigu, Shugenja). Readings from the game's own furigana where it gives them.
- Credits: English.
- Register / flavour: Heian period fantasy. Light archaic flavour in speech, never Ye Olde: no thee/thou, no "-eth".
  Elders and nobles speak formally ("I had thought you would come", "Is that not so?"), commoners and children plain.
  Sound effects: *Slam!* style is not used in this script; screams and cries stay short ("Aaah!").
- Abbreviations: full names and terms everywhere, prefer engine changes over shortening (D4, D10, D11).

## Style rules
- Punctuation map: 「」 -> "...", 『』 -> '...', ・・ / ・・・ / ・・・・・・ -> ... (one ellipsis, three dots), ！？ -> ?!,
  ！！ -> ! (or !! when shouting), ーっ (drawn-out cry) -> repeated letter or "!" ("Kagura!", "Waaait!").
- English text is plain ASCII. No curly quotes, no em dash (use " - " sparingly or a comma), no `~`.
- Layout: `{br}` = new line in the box, `{page}` = new box (key press). Lines are re-flowed freely: English breaks
  where it reads best, not where the Japanese broke. Never leave a last line under 6 characters.
- `{name}` and `{num}` stay; the game draws a name or number there. No "a/an" right before `{name}`, no suffix
  glued on it ("{name}'s" is fine), never "{num}th"; write "No. {num}".
- Furigana in the Japanese text (道摩（どうま）) is a reading aid: the English gives the name once, no parentheses.
- Spell names, items and places inside dialogue use the table forms below, capitalised.
- Voice: see `docs/style-reference.md`.

## Characters (party: short form in the 40-px party slot; full form in name fields)
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 神楽 | Kagura | 40 narrow | the hero: a BOY of 16 (he/him, id 295 男子), raised by Tenkai at Kumano | |
| 芦屋道満 | Ashiya Doman | | Seimei's disciple (prologue 2A2) | |
| 花山帝 / 花山天皇 | Emperor Kazan | | in the prologue (984-985); later the Retired Emperor Kazan | |
| 為光 | Tamemitsu | | Major Counselor Fujiwara no Tamemitsu, Lady Kishi's father | |
| 女官 | Lady-in-waiting | | | |
| 道長 | Michinaga | | Fujiwara no Michinaga, the regent (2A8) | |
| 宮司 | Chief Priest | | of Kumano (2E8); 宮司殿 = Chief Priest-dono | |
| 安倍晴明 | Abe no Seimei | | the script spells him both 安部 and 安倍 | |
| 安部晴明 / 晴明 | Abe no Seimei / Seimei | 48 field | the great onmyoji; old, formal, wry | Abe Seimei |
| 賀茂広行 / 広行 | Kamo no Hiroyuki / Hiroyuki | | onmyoji, Seimei's colleague; earnest, formal | |
| 藤原盛高 / 盛高 | Fujiwara no Moritaka / Moritaka | | | |
| 上宮 | Jogu | | | |
| 紅葉 | Momiji | | Togakushi | |
| 蝉丸 | Semimaru | | biwa priest | |
| 卯月 | Uzuki | | Ise Saigu priestess (斎宮卯月 = Saigu Uzuki) | |
| 蘆太 | Ashita | | | |
| 桔梗 | Kikyo | | | |
| 楓 | Kaede | | | |
| 葵 | Aoi | | | |
| 金剛坊 / 金剛 | Kongobo / Kongo | | tengu | |
| 虚空坊 / 虚空 | Kokubo / Koku | | tengu | |
| 狗法眼 / 狗法 | Kuhogen / Kuho | | | |
| 猿法眼 / 猿法 | Enhogen / Enho | | | |
| 夷 | Ebisu | | | |
| 春菜 | Haruna | | | |
| 飛騨 | Hida | | person; the province is also Hida | |
| 雀 | Suzume | | | |
| 雉女 | Kijime | | | |
| 葉月 | Hazuki | | | |
| 愛深 | Aimi | | | |
| 珍念 | Chinnen | | | |
| 如雲 | Joun | | | |
| 沙摩 | Shama | | | |
| 不動 | Fudo | | | |
| 普賢 | Fugen | | | |
| 法蓮 | Horen | | | |
| 照雲 | Shoun | | | |
| 多聞 | Tamon | | | |
| 六角 | Rokkaku | | | |
| 源信 | Genshin | | | |
| 仁空 | Ninku | | | |
| 橘諸秀 / 諸秀 | Tachibana no Morohide / Morohide | | | |
| 源頼光 / 頼光 | Minamoto no Yorimitsu / Yorimitsu | | | Raiko |
| 渡辺綱 | Watanabe no Tsuna | | short form 綱 = Tsuna | |
| 田辺景時 / 景時 | Tanabe Kagetoki / Kagetoki | | | |
| 越智正秀 / 正秀 | Ochi Masahide / Masahide | | | |
| 坂田公時 / 公時 | Sakata no Kintoki / Kintoki | | | |
| 碓井貞光 / 貞光 | Usui Sadamitsu / Sadamitsu | | | |
| 伴為之 / 為之 | Tomo no Tameyuki / Tameyuki | | | |
| 藤原保昌 / 保昌 | Fujiwara no Yasumasa / Yasumasa | | | |
| 佐伯琴乃 / 琴乃 | Saeki Kotono / Kotono | | | |
| 源頼信 / 頼信 | Minamoto no Yorinobu / Yorinobu | | | |
| 杉丸 | Sugimaru | | | |
| 藤原高遠 / 高遠 | Fujiwara no Takato / Takato | | | |
| 卜部季武 / 季武 | Urabe no Suetake / Suetake | | | |
| 天海 | Tenkai | | priest at Kumano, Kagura's foster father (天海和尚 = Priest Tenkai) | |
| 道摩 | Doma | | Seimei's former disciple, missing 15 years | Dōma |
| 偽道摩 | False Doma | | | |
| 平将門 / 将門 | Taira no Masakado / Masakado | | rebel dead 60 years | |
| 藤原純友 / 純友 | Fujiwara no Sumitomo / Sumitomo | | | |
| 阿古耶 | Akoya | | | |
| 調伏丸 | Chobukumaru | | | |
| 相模入道 | Sagami Nyudo | | | |
| 久慈法眼 | Kuji Hogen | | | |
| 日下法眼 | Kusaka Hogen | | | |
| 小野正光 | Ono no Masamitsu | | | |
| 真叉陀 | Shinshada | | | |
| 霞隠鬼 / 霞陰鬼 | Kainki | | | |
| 磯目鬼 | Isomeki | | | |
| 兎乃 | Usagino | | Akana's wife | |
| 葛葉 | Kuzunoha | | | |
| 赤名 | Akana | | brothers holding the Shikoku barrier | |
| 緑名 | Midorina | | | |
| 青名 | Aona | | | |
| 石上 | Isogami | | | |
| 守屋 | Moriya | | | |
| 八十物部 | Yaso Mononobe | | | |
| 藤太 | Tota | | | |
| 祇子 | Kishi | | 女御祇子 = Lady Kishi, an imperial consort | |
| 花山法皇 | Retired Emperor Kazan | | 法皇 alone = the Retired Emperor | |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 京の都 | Kyoto | 48 field | 都 alone in speech = "the capital" | |
| 安部野 / 安倍野 | Abeno | | | |
| 熊野本宮 | Kumano Hongu | | 熊野 = Kumano | |
| 熊野 | Kumano | | | |
| 伊勢斎宮 | Ise Saigu / Ise Priestess | | the shrine; as a person/class: Ise Priestess | |
| 高野山 | Mount Koya | | 高野 = Koya | |
| 比叡山 | Mount Hiei | | | |
| 丹後国分寺 | Tango Kokubunji | | | |
| 戸隠 | Togakushi | | 戸隠の里 = Togakushi Village | |
| 出雲 | Izumo | | | |
| 逢坂峠 | Osaka Pass | | | |
| 伊和峠 | Iwa Pass | | | |
| 大江山 | Mount Oe | | | |
| 四国 | Shikoku | | | |
| 淡路 | Awaji | | | |
| 伊予 | Iyo | | | |
| 内裏 | the Palace | | the imperial palace | |
| 山陰道 | San'indo | | 山陽道 = San'yodo | |
| 加太 | Kada | | ferries: Kada / Ishikuma / Awaji / Minotsu / Sakaide / Iyo Ferry | |
Provinces 24A-288: the old province name alone (Musashi, Sagami); 北部/南部/東部/西部 = North/South/East/West
Echigo. 安房 = "Awa (Boso)", 阿波 = Awa.

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 式神 | shikigami | | spirits summoned by onmyoji (plural shikigami) | familiar |
| 陰陽師 | onmyoji | | capitalised only as a class name | yin-yang master |
| 陰陽道 | Onmyodo | | | |
| 結界 | barrier | | | kekkai |
| 部隊 | Squad | | in names ("Kagura Squad"); "squad/unit" in prose | |
| 山童 | Yamawaro | | mountain-child folk; 山童隊長 = Yamawaro Captain | |
| 死人返し | Raising the Dead | | Doma's forbidden rite | |
| 移転の法 | Rite of Transference | | 大法術 of the Yamawaro | |
| 検非違使 | Kebiishi | | the capital police | |
| 呪禁道師 | Jugon Master | | class | |
| 修験道師 | Shugenja | | class | |
| 琵琶法師 | Biwa Priest | | class | |
| 天狗 | tengu | | | |
| 鬼 | oni | | demon of folklore; "oni" not "ogre" | ogre |
| 妖魔 | yokai | | | |
| 法印 | Seal | | jutsu names: 火天法印 = Katen Seal etc. | |
| 言霊 | Kotodama | | | |
| 辺津の鏡 | Hetsu Mirror | | key item, shows the map | |
| 立向盤 | Tatemuki Board | | key item, opens Iyo | |
| 反魂法珠 | Hangon Jewel | | key item, breaks Masakado's barrier | |
Item, jutsu, shikigami, enemy and class names: the `en` of rows 001-1C4 in `script/C3.tsv` are binding; use them
verbatim when dialogue names one (`build/terms_bNNN.txt` lists the ones a batch needs).

## Decisions from earlier batches
- wave 0 (terms): 水龍剣 -> Water Dragon Blade (two 8-px lines of 48 px); 淡路藤原家 -> Fujiwara Manor, Awaji;
  降魔邪法 -> Demon Quelling; 独鈷杵/三鈷杵/五鈷杵/七鈷杵 -> 1/3/5/7-Prong Vajra.
- b001: one-line battle messages hold a unit name of up to ~118 px, leaving ~58 px: terse forms ("{name} fell!",
  "{name}: no effect", "{name} paralyzed"). 227 uses a `{br}` ("Shikigami sealed:{br}{name}"): check it in battle
  in phase 8. Years: 永観二年（９８４） -> "Eikan 2 (984)". 伊予守 -> Governor of Iyo, 河内の国守 -> Governor of Kawachi.
- b002: 藤太 -> Tota (Kagura's companion from Kumano). Tenkai calls Kagura "my boy".
