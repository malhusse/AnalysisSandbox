#!/bin/bash

# cd /home/mo/Analysis/AnalysisTools/train0/
# optirun python -u train_hmm.py >> output.log 

cd /home/mo/Analysis/AnalysisTools/train1/
optirun python -u train_hmm.py >> output.log

cd /home/mo/Analysis/AnalysisTools/train5/
optirun python -u train_hmm.py >> output.log

# cd /home/mo/Analysis/AnalysisTools/train2/
# optirun python -u train_hmm.py >> output.log

# cd /home/mo/Analysis/AnalysisTools/train3/
# optirun python -u train_hmm.py >> output.log

# cd /home/mo/Analysis/AnalysisTools/train4/
# optirun python -u train_hmm.py >> output.log

systemctl suspend
