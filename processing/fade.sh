for i in ../data/auto-cut/*.wav; do
	base_name=$(basename $i)
	ffmpeg -y -i $i -af "afade=d=1, areverse, afade=d=1, areverse" "../data/faded/$base_name";
done

for i in ../data/manual-cut/*.wav; do
	base_name=$(basename $i)
	ffmpeg -y -i $i -af "afade=d=1, areverse, afade=d=1, areverse" "../data/faded/$base_name";
done