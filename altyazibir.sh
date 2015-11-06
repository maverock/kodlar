echo $1
cikis="/home/birim/"
dosya="${1%.*}"
deneme=${1%%mkv}
srt="$deneme""srt"
#iconv -t UTF-8 -f ISO-8859-9 "$srt" > "${srt}s"
#mv "${srt}s" "${srt%.srts}"
sudo mkvmerge -o "$cikis""$dosya""mkv" -S "$1" "$srt"
