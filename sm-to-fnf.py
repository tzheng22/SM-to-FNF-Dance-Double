c = 0
with open("newfile.txt", "r") as f:
    together_old = f.read().split(",")
    f.close()
together = []
while c < len(together_old):
    together.append(together_old[c].replace("\n", ""))
    c += 1

with open("bpms.txt", "r") as f:
    bpmsTimestamps = f.read().splitlines()

bpm = []
timestamps = []

for i in bpmsTimestamps:
    temp = i.split("=")
    timestamps.append(temp[0])
    bpm.append(temp[1])

currentBPMIndex = 0
currentBPM = float(bpm[currentBPMIndex])
millisecondsPerBeat = 60000 / currentBPM

notes = []
bpmofnotes = []

currBeatInMilliSeconds = 0
currBeat = 0

measure = 0
hold = [0, 0, 0, 0, 0, 0, 0, 0]
holdtimestamp = [0, 0, 0, 0, 0, 0, 0, 0]
counthold = [False, False, False, False, False, False, False, False]
while measure < len(together):
    line = 0
    if currentBPMIndex < len(timestamps) - 1 and float(timestamps[currentBPMIndex + 1]) == round(currBeat, 3):
        currentBPMIndex += 1
        currentBPM = float(bpm[currentBPMIndex])
        millisecondsPerBeat = 60000 / currentBPM
    while line < len(together[measure]) / 8:
        lane = 0
        while lane < 8:
            if counthold[lane]:
                hold[lane] += millisecondsPerBeat / 48
            if together[measure][8 * line + lane:8 * line + lane + 1] == "1":
                notes.append([currBeatInMilliSeconds, lane, 0, 0])
            if together[measure][8 * line + lane:8 * line + lane + 1] == "M":
                notes.append([currBeatInMilliSeconds, lane, 0, 3])
            if together[measure][8 * line + lane:8 * line + lane + 1] == "2":
                counthold[lane] = True
                holdtimestamp[lane] = currBeatInMilliSeconds
            if together[measure][8 * line + lane:8 * line + lane + 1] == "3":
                counthold[lane] = False
                noteIndex = 0
                while noteIndex < len(notes) and round(holdtimestamp[lane], 6) > round(notes[noteIndex][0], 6):
                    noteIndex += 1
                if noteIndex == len(notes):
                    notes.append([holdtimestamp[lane], lane, hold[lane], 0])
                else:
                    notes.insert(noteIndex, [holdtimestamp[lane], lane, hold[lane], 0])
                hold[lane] = 0
                holdtimestamp[lane] = 0
            lane += 1
        currBeatInMilliSeconds += millisecondsPerBeat / 48
        currBeat += 1 / 48
        line += 1
    changeBPM = currentBPMIndex > 0 and currentBPM != bpm[currentBPMIndex - 1]
    if changeBPM:
        changeBPM = "true"
    else:
        changeBPM = "false"
    bpmofnotes.append([currentBPM, changeBPM])
    measure += 1

sectionNotesCollection = []
for measure in together:
    sectionNotesCollection.append([])
currentBPMIndex = 0
currentBPM = float(bpm[currentBPMIndex])
millisecondsPerBeat = 60000 / currentBPM
totalLengthOfSong = currBeatInMilliSeconds
currBeatInMilliSeconds = 0
currBeat = 0
measure = 0
noteIndex = 0
while measure < len(sectionNotesCollection):
    if currentBPMIndex < len(timestamps) - 1 and float(timestamps[currentBPMIndex + 1]) == currBeat:
        currentBPMIndex += 1
        currentBPM = float(bpm[currentBPMIndex])
        millisecondsPerBeat = 60000 / currentBPM
    measureLength = millisecondsPerBeat * 4
    while noteIndex < len(notes) and round(notes[noteIndex][0], 6) < round(measureLength + currBeatInMilliSeconds, 6):
        sectionNotesCollection[measure].append(notes[noteIndex])
        noteIndex += 1
    measure += 1
    currBeat += 4
    currBeatInMilliSeconds += measureLength

u = 0
jsondump = []
while u < len(sectionNotesCollection):
    if u < len(sectionNotesCollection) - 1:
        jsondump.append(
            "{\n" + f"\"sectionNotes\":{str(sectionNotesCollection[u])},\n\"lengthInSteps\": 16,\n\"bpm\": {bpmofnotes[u][0]},\n\"changeBPM\": {bpmofnotes[u][1]},\n\"mustHitSection\": false" + "\n},\n")
    else: # bc stupid ass json breaks if theres an extra comma
        jsondump.append(
            "{\n" + f"\"sectionNotes\":{str(sectionNotesCollection[u])},\n\"lengthInSteps\": 16,\n\"bpm\": {bpmofnotes[u][0]},\n\"changeBPM\": {bpmofnotes[u][1]},\n\"mustHitSection\": false" + "\n}\n")
    u += 1
yourMom = input("song name? ").replace(" ", "-")
difficulty = input("difficulty? (blank if normal) ").replace(" ", "-")
if difficulty:
    difficulty = "-" + difficulty
output = open(f"{yourMom + difficulty}.json", "w")
output.write(
    "{\n\"song\": {\n\"sectionLengths\": [],\n\"player1\": \"bf\",\n\"events\": [],\n\"gfVersion\": \"gf\",\n\"notes\": [\n")
for i in jsondump:
    output.write(i)
output.write(
    "],\n\"player2\": \"dad\",\n\"player3\": null,\n\"song\": \"" + yourMom + "\",\n\"validScore\": true,\n\"stage\": \"stage\",\n\"sections\": 0,\n\"needsVoices\": true,\n\"speed\": 3.5,\n" + f"\"bpm\": {bpm[0]}\n" + "}\n}")
output.close()
