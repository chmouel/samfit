;;; Directory Local Variables
;;; For more information see (info "(emacs) Directory Variables")

((nil .
      ((multi-compile-alist
        (python-mode
         ("zwift-generate-zwo" . "python3 ${HOME}/Dropbox/Documents/Fitness/traineroad/soft/main.py zwift_generate_zwo --output_dir=/tmp  108543 102801")
         ("get-calendar-workout" . "python3 -E ${HOME}/Dropbox/Documents/Fitness/traineroad/soft/main.py tp_get_calendar_workouts 'Monday 07 January 2019' 'Sunday 30 Jun 2019' 'Ironman-Training'")
         ("tp-generate-ical" . "python3 -E ${HOME}/Dropbox/Documents/Fitness/traineroad/soft/main.py tp_calendar_workouts_ical --calendar-title=\"Ironman Nice Training 2019\" --generated-output-file='Ironman-Training' 'Monday 14 January 2019' 'Sunday 30 Jun 2019' '/tmp/Ironman-Training.ics'")
         ("plan-to-ical" . "python3 -E ${HOME}/Dropbox/Documents/Fitness/traineroad/soft/main.py plan_to_ical TP-Ironman-Training 'Ironman Nice Training 2019' 'Monday 14 January 2019' /tmp/Ironman-Training.ics")
         ("show-plan" . "/usr/local/bin/python3 -E ${HOME}/Dropbox/Documents/Fitness/traineroad/soft/main.py show_plan TP-Ironman-Training")
         ("show-plan-sync" . "/usr/local/bin/python3 -E ${HOME}/Dropbox/Documents/Fitness/traineroad/soft/main.py show_plan TP-Ironman-Training --start-date='Monday 14 January 2019' --sync-garmin-today ")
         ("get-plan" . "python3 -E ${HOME}/Dropbox/Documents/Fitness/traineroad/soft/main.py tr_get_plan -p 157")
         ("generate-md" . "python3 -E ${HOME}/Dropbox/Documents/Fitness/traineroad/soft/main.py tr_generate_md --markdown-dir /tmp/md -p 157 ")
         ("import-plan" . "python3 -E ${HOME}/Dropbox/Documents/Fitness/traineroad/soft/main.py tp_import_plan TP-Ironman-Training 'Monday 07 January 2019'")
         ("plan-to-tp-samfit" . "python3 -E '/Users/chmouel/Dropbox/Documents/Fitness/traineroad/soft/main.py' --tp-user=samfit tr_plan_to_tp -p 149 --start-date 'Monday 3 December 2018'")
         ("unimport-plan" . "python3 -E '/Users/chmouel/Dropbox/Documents/Fitness/traineroad/soft/main.py' tr_unapply_plan_on_tp -p 146 --start-date 'Monday 14 October 2019'")
         )))))
