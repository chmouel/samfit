# -*- coding: utf-8 -*-
# Author: Chmouel Boudjnah <chmouel@chmouel.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
BasePhase = {
    "Sweet Spot": {
        "description": """Sweet Spot Base has two consecutive six-week blocks: I and II.  Time
        permitting, complete each block in order.  The Sweet-Spot block is the
        most efficient form of base training for 99% of cyclists — it’s what we
        recommend.  You’ll train in the Sweet-Spot, Threshold and VO2max power
        zones for a blend of interval training that makes you stronger, faster.
        Aside from the significant fitness gains and increases in FTP, you’ll
        enhance your form work and pedaling mechanics.  If you have the time and
        prefer the traditional style but would like to complete this block, the
        high-volume block incorporates aspects of both Sweet-Spot and
        Traditional base training.
        """,
        "Low Volume 1": 145,
        "Low Volume 2": 146,
        "Mid Volume 1": 147,
        "Mid Volume 2": 148,
        "High Volume 1": 149,
        "High Volume 2": 150,
    },
    "Sprint Distance Triathlon": {
        "description": """Sprint triathlons require a very different approach than the
        increasingly common Half- and Full-Distance triathlons.  The short
        duration of these events generally requires a high-level of intensity —
        something to start training for from the beginning.""",
        "Low Volume": 210,
        "Mid Volume": 211,
        "High Volume": 212,
    },
    "Olympic Distance Triathlon": {
        "description": """
        Effectively managing your training time begins to get difficult when you
        step into the Olympic distance.  It is crucial for athletes competing in
        this international distance to develop their threshold power in all
        disciplines, since this is where they will spend most of their time on
        race day.
        """,
        "Low Volume": 213,
        "Mid Volume": 214,
        "High Volume": 215,
    },
    "Half Distance Triathlon": {
        "description": """
        Athletes training for half-distance triathlons need to build a broad
        aerobic base while paying attention to intensities at or above
        threshold.  Whether you are a time-constrained athlete, or somebody
        looking to PR their next event with plenty of available training time,
        these plans will effectively build your endurance in all three triathlon
        disciplines.
        """,
        "Low Volume": 216,
        "Mid Volume": 217,
        "High Volume": 218,
    },
    "Full Distance Triathlon": {
        "description": """
        Although full-distance triathlons are considered an endurance event, the
        low-volume variation of this plan still gives you the fitness you need
        in the always-critical Base Phase.  Ranging from 4-5 days of training
        per week, this plan will take 12 weeks to establish a lasting and
        reliable base of aerobic fitness.
        """,
        "Low Volume": 219,
        "Mid Volume": 220,
        "High Volume": 221,
    },
    "Traditional": {
        "description": """Traditional Base has three consecutive four-week blocks: I, II and
        III.  Time permitting, complete each block in order.

        As its name implies, the Traditional block takes the old-fashioned
        approach to base training.  It requires a large time commitment to give
        you significant gains.  Unless you have at least 10 hours/week to train,
        we do not recommend the long, low-intensity Traditional approach.
        Workouts include fair shares of form work, pedaling drills, power
        sprints, force intervals and hill simulations.

        This block is primarily geared toward Grand Tour athletes or those
        recovering from an injury who want to avoid high-intensity intervals.
        """,
        "Low Volume 1": 123,
        "Low Volume 2": 126,
        "Low Volume 3": 129,
        "Mid Volume 1": 124,
        "Mid Volume 2": 127,
        "Mid Volume 3": 130,
        "High Volume 1": 125,
        "High Volume 2": 128,
        "High Volume 3": 131,
    },
}
BuildPhase = {
    "Short Power": {
        "description": """Riders undertaking the Short Power approach will still face their
        fair share of muscle endurance work, but the reduction in sustainable
        power focus is directed into a further emphasis in VO2 Max - less muscle
        endurance, more max aerobic power.

        The Short Power Build blocks were developed with a slightly different
        breed of rider in mind.  Riders who need a more balanced mix of
        sustainable power, short/high power or really short/really high power.
        Criterium racers, cyclocross competitors and nearly all forms of
        mountain bike & track riders will be well served by the Short Power
        Build.
        """,
        "Low Volume": 151,
        "Mid Volume": 152,
        "High Volume": 153,
    },
    "General Power": {
        "description": """For riders who simply don’t want to label themselves as steady-state
        or short-power athletes, the General Build blocks blend all types of
        power with the aim of building higher forms of conditioning very evenly.
        This most-balanced combination of sought after training adaptations was
        created in order to prepare riders for the demands they’ll face on the
        road & the dirt.

        These blocks target all-around riders competing in stage races - whether
        on the road or the dirt - road racers that face traditional rolling
        courses, and “combination riders” who like to dabble in a number of
        disciplines over the course of each year.""",
        "Low Volume": 154,
        "Mid Volume": 155,
        "High Volume": 156,
    },
    "Sustained Power": {
        "description": """The Sustained Power Build blocks place more emphasis on developing
        greater sustained power through the use of strength endurance work,
        lactate tolerance workouts & a healthy dose of maximum aerobic power
        intervals.

        These specific blocks were constructed with riders of a more
        steady-state nature in mind; riders who don’t necessarily face as many
        short-power demands.  Multisport athletes, time trial specialists,
        century & gran fondo riders, and road racers (climbing) are all
        Sustained Power candidates.""",
        "Low Volume": 157,
        "Mid Volume": 158,
        "High Volume": 159,
    },
    "Sprint Triathlon": {
        "description": """
        Having recently covered the necessary sprint-specific yet
        triathlon-general training, these short-duration Build blocks take the
        next step in preparing triathletes for the short, intense nature of the
        triathlons quickest format.
        """,
        "Low Volume": 222,
        "Mid Volume": 223,
        "High Volume": 224,
    },
    "Olympic Triathlon": {
        "description": """
        In the pursuit of raising and then sustaining threshold power & pace in
        all 3 disciplines, these Build blocks shape the Olympic format training
        demands further by elevating all workout requirements and bringing them
        more in line with race-day intensities.
        """,
        "Low Volume": 225,
        "Mid Volume": 226,
        "High Volume": 227,
    },
    "Half Distance Triathlon": {
        "description": """
        Furthering the ability to sustain race efforts that lean a little more
        toward speed than full-distance events, these training blocks push the
        strength-endurance requirements noticeably higher than the previous Base
        blocks.
        """,
        "Low Volume": 228,
        "Mid Volume": 229,
        "High Volume": 230,
    },
    "Full Distance Triathlon": {
        "description": """
        Full-distance events first require base fitness, and a lot of it.  With
        that in place, it's now time to start building your sustainable power on
        the bike as well as your fast but maintainable run & swim paces such
        that race-day speeds will be noticeably faster than they currently are.
        """,
        "Low Volume": 231,
        "Mid Volume": 232,
        "High Volume": 233,
    },
}
SpecialityPhase = {
    "Road": {
        "Rolling Road Race": {
            "description": """
            The demands of rolling road races are often more wide-ranging than
            races including long, sustained climbs.  Riders face recurrent
            flurries of attacks & counterattacks in any road race, but when the
            course undulates with more frequent & shorter climbs, even breakaway
            riders find themselves exerting widely varied efforts over the
            course of their races.

            So the aim here is to increase Sprint & Anaerobic power in addition
            to improving power & time at VO2 Max while also maintaining your
            base, aerobic Endurance fitness.
            """,
            "Low Volume": 168,
            "Mid Volume": 169,
            "High Volume": 170,
        },
        "Climbing Road Race": {
            "description": """
            Climbing road races differ from flat ones in obvious ways - they
            usually include sustained climbs, and often finish on one - but they
            also share a lot of overlap with flat or rolling road races.

            As you might expect, the Climbing Road Race blocks address this
            diversity with a heavier emphasis on sustained power than short
            power, with due attention still paid to maintaining your base of
            aerobic endurance.

            So if your races involve selective climbs, if you have to be able to
            hold high percentages of your FTP after hours of already challenging
            ride time, and if you want road-race fitness that favors longer,
            sustained efforts, the Climbing Road Race blocks are ideal for you.
            """,
            "Low Volume": 171,
            "Mid Volume": 172,
            "High Volume": 173,
        },
        "Criterium": {
            "description": """
            The demands of criterium racing are similar to those of cyclocross &
            XC MTB races.  This overlap in performance requirements leads to a
            reutilization of workouts across these 3 disciplines and addresses
            not only a need for aerobic as well as anaerobic endurance but also
            sprint timing & capacity.

            You'll face workouts that grow increasingly crit-like in their
            demands by furthering your ability to generate high watts for short
            periods of time, over & over & over again with little & sometimes
            blink-and-you'll-miss-it recovery durations.

            If you like your races to be of the highest intensity & often very
            technical, if you thrive on highly strategic, non-stop and
            exceptionally painful crowd-pleasers, then the Criterium specialty
            blocks are exactly what you'll need to get you ready to tolerate &
            dole out this brand of physical abuse.
            """,
            "Low Volume": 174,
            "Mid Volume": 175,
            "High Volume": 176,
        },
        "40k TT": {
            "description": """
            Whether in the pursuit of the esteemed sub-hour or the nearly
            mythical sub-50 40k TT, a time trialist has to first be fast, then
            be fast over the required distance and then do both while riding in
            a less-than-comfortable aerodynamic position.

            Much of these demands are physical but an under-credited aspect of
            racing the clock is the simple matter of being tough & accustomed to
            suffering.  Add to this the requisite ability to effectively &
            intelligently pace a single, relatively long effort, and the
            apparent simplicity of a time trial evaporates.

            Accordingly, our multifaceted approach works to build a body capable
            of maintaining your highest sustainable power, forges a mind capable
            of tolerating high levels of discomfort while consciously pacing
            well and finally dresses it all in increasing levels of
            aerodynamics.
            """,
            "Low Volume": 198,
            "Mid Volume": 199,
            "High Volume": 200,
        },
        "Century": {
            "description": """
            Focused entirely on fostering a high level of muscular endurance,
            one that allows you to push the pedals powerfully and for many hours
            at a time, each version of the Century training blocks include
            workouts ranging from Sweet Spot to VO2max efforts to continually
            monitor (and further) your progress.  The option for an increasingly
            long, weekend Endurance ride is included in the ‘Week Tips’ if you
            prefer a long, low-intensity approach on the weekend.

            If long days in the saddle suit you and you want the type of fitness
            that allows you to ride them faster or simply enjoy them that much
            more, these plans are what you’re looking for.
            """,
            "Low Volume": 201,
            "Mid Volume": 202,
            "High Volume": 203,
        },
    },
    "Triathlete": {
        "Sprint Distance Triathlon": {
            "description": """
            These highly specific and very often intense training blocks are the
            final step in any sprint triathletes specialized training leading up
            to their most important, very short, potentially very fast
            triathlon(s).
            """,
            "Low Volume": 234,
            "Mid Volume": 235,
            "High Volume": 236,
        },
        "Olympic Distance Triathlon": {
            "description": """Having built the necessary ability to not only work hard but to
            work hard for longer periods of time, it's now vital that you hone
            your capabilities to a point that allows you to race your fastest on
            the days that matter most.""",
            "Low Volume": 237,
            "Mid Volume": 238,
            "High Volume": 239,
        },
        "Half Distance Triathlon": {
            "description": """With the necessary endurance & strength in the bank, the
            objective becomes growing as familiar as possible with the very
            specific demands of racing long but not really long.  This
            challenging mix of speed & endurance demands the very particular
            preparation offered over the course of this final pre-race block of
            training.
            """,
            "Low Volume": 240,
            "Mid Volume": 241,
            "High Volume": 242,
        },
        "Full Distance Triathlon": {
            "description": """
            Athletes nearing the culmination of their ultra-distance training
            can now shift their focus to the fine-tuning of their abilities
            lumped together with distances & paces very much in line with their
            race-day demands.
            """,
            "Low Volume": 243,
            "Mid Volume": 244,
            "High Volume": 245,
        },
    },
    "Enthusiast": {
        "Maintenance": {
            "description": """Not everyone who rides a bike has a
            specific goal or event in mind.  Perhaps you don’t have the time, or
            desire, to repeat your Specialty training plan, or maybe you simply
            want some nicely-varied, high-intensity workouts to keep you sharp,
            keep you fit.

            The pillars of all our interchangeable HIT Maintenance training
            blocks are three high-intensity workouts with the option to
            incorporate some additional lower-intensity workouts based on your
            weekly training volume.  Expect to work hard, really hard, but then
            recover as you see fit by shaping these interchangeable Maintenance
            plans to fit your race or non-competitive schedule.""",
            "Low Volume 1": 160,
            "Low Volume 2": 161,
            "Mid Volume 1": 162,
            "Mid Volume 2": 163,
            "High Volume 1": 164,
            "High Volume 2": 165,
        },
        "Time Crunch 30": {
            "description": """
            Perhaps sad to say, but we don’t all have enough time to train like
            the pro’s.  Some of us don’t even have the time to train like
            weekend warriors, and some barely have enough time to get on the
            bike for a half hour a few times a week.

            The 30-minute workouts that comprise the Time Crunch 30 blocks are
            modeled after some of our most popular 60-minute workouts offering
            shorter but no less intense efforts in order to grant time-crunched
            athletes the luxury of a similar training effect, just in less time.
            """,
            "Low Volume": 166,
            "Mid Volume": 167,
        },
        "Time Crunch 45": {
            "description": """Riders still crunched for time but with the luxury an extra 15
            minutes to devote to the bike - working, not warming - can get a
            massive training benefit out of repeating a handful of 45-minute
            interval workouts each week.

            Every workout constituting the Time Crunch 45 plans are slightly
            shortened versions of many of our most popular 60-minute workouts
            which then trim off enough work to get you on & off the bike inside
            of a single hour.  Less time per workout, less time per week, and
            you'll still see measurable levels of performance improvement.""",
            "Low Volume": 246,
            "Mid Volume": 247,
        },
    },
}
Category = {"Base": BasePhase, "Build": BuildPhase, "Speciality": SpecialityPhase}
