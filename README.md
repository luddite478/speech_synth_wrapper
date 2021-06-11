![alt text](architecture.png?raw=true)

## To synth voice:
1. Run main.py
2. Set input text file path in the input_text_file DAT of voicesynth.toe 
3. Set output folder in text_to_speech/meta DAT (playlist folder) of voicesynth.toe
4. Save text file

## Available line options: ["v"="","e"="","s"="","l"="",p=""]
# v - voice 
* oksana	ru-RU	Ж
* jane	ru-RU	Ж
* omazh	ru-RU	Ж
* zahar	ru-RU	M
* ermil	ru-RU	M
* silaerkan	tr-TR	Ж
* erkanyavas	tr-TR	M
* alyss	en-US	Ж
* nick	en-US	M

# e - emotion
* good 
* evil 
* neutral \
Only for (ru-RU) и voices jane or omazh.

# s - speed
0.1 - 3.0

# l - language
* ru-RU
* en-EN
* tr-TR

# p - pitch
* 0 - N

## TODO:
Add other voice synths (works only with yandex at the moment)
