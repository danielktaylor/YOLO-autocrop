for file in ./images/*; do
    if [[ -f "$file" && $(identify -format "%wx%h" "$file") == "800x600" ]]; then
        convert "$file" -gravity center -background black -extent 800x800 "$file"
    fi
done