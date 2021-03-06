import sqlite3
import pandas as pd
from haversine import haversine
import itertools
import numpy
import random

north_pole = (90, 0)
weight_limit = 1000  # 1000.0

for i in range(90, -90, int(-180 / 1.26)):  ##Other split
    print("i=: " + str(i))

for i in range(180, -180, int(-360 / 1.4)):  ##Other split
    print("i=: " + str(i))


def bb_sort(ll):
    s_limit = 7000
    optimal = False
    ll = [[0, north_pole, 10]] + ll[:] + [[0, north_pole, 10]]
    while not optimal:
        optimal = True
        for i in range(1, len(ll) - 4):
            lcopy = [[] for _ in range(15)]  # [0] not used
            b = list(itertools.permutations(([0, 1, 2, 3])))

            for k in range(1, 15):
                lcopy[k] = ll[:]
                lcopy[k][i], lcopy[k][i + 1], lcopy[k][i + 2], lcopy[k][i + 3] = ll[i + b[k][0]][:], ll[i + b[k][1]][:], \
                                                                                 ll[i + b[k][2]][:], ll[i + b[k][3]][:]

            minDist = pathlength(ll[1:-1])
            kmn = 0
            for k in range(1, 15):
                tmp = pathlength(lcopy[k][1:-1])
                if tmp < minDist:
                    kmn = k
                    minDist = tmp
            if kmn > 0:
                # print("swap")
                ll = lcopy[kmn][:]
                optimal = False
                s_limit -= 1
                if s_limit < 0:
                    optimal = True
                    break
                continue

    return ll[1:-1]


def optimizetrips(trip1):

    bb_sort(trip1)

    bestTrip = trip1[:]
    for i in range(1000):
        r11 = random.randint(0, len(trip1)-1)
        r12 = random.randint(0, len(trip1)-1)
        #
        temp1 = trip1[r11]
        trip1[r11] = trip1[r12]
        trip1[r12] = temp1

        if pathlength(trip1) < pathlength(bestTrip):
            bestTrip = trip1[:]

    return bestTrip


def pathlength(llo):
    f_ = 0.0
    d_ = 0.0
    l_ = north_pole
    for i in range(len(llo)):
        d_ += haversine(l_, llo[i][1])
        f_ += d_ * llo[i][2]
        l_ = llo[i][1]
    d_ += haversine(l_, north_pole)
    f_ += d_ * 10  # sleigh weight for whole trip
    return f_


gifts = pd.read_csv("../input/gifts.csv").fillna(" ")
c = sqlite3.connect(":memory:")
gifts.to_sql("gifts", c)

cu = c.cursor()
cu.execute("ALTER TABLE gifts ADD COLUMN 'TripId' INT;")
cu.execute("ALTER TABLE gifts ADD COLUMN 'i' INT;")
cu.execute("ALTER TABLE gifts ADD COLUMN 'j' INT;")
c.commit()

for n in [1.25252525]:
    i_ = 0
    j_ = 0
    for i in range(90, -90, int(-180 / n)):  ##Other split
        i_ += 1
        j_ = 0
        for j in range(180, -180, int(-360 / (n + 0.0))):  ##Other split
            j_ += 1
            cu = c.cursor()
            cu.execute("UPDATE gifts SET i=" + str(i_) + ", j=" + str(j_) + " WHERE ((Latitude BETWEEN " +
                       str(i - (180 / n)) + " AND  " + str(i) + ") AND (Longitude BETWEEN " + str(j - (360 / n)) +
                       " AND  " + str(j) + "));")
            c.commit()

    for limit_ in [66]:
        trips = pd.read_sql(
            "SELECT * FROM (SELECT * FROM gifts WHERE TripId IS NULL ORDER BY i, j, Longitude, Latitude LIMIT " +
            str(limit_) + " ) ORDER BY Latitude DESC", c)
        t_ = 0
        while len(trips.GiftId) > 0:
            g = []
            t_ += 1
            w_ = 0.0
            for i in range(len(trips.GiftId)):
                if (w_ + float(trips.Weight[i])) <= weight_limit:
                    w_ += float(trips.Weight[i])
                    g.append(trips.GiftId[i])
            cu = c.cursor()
            cu.execute("UPDATE gifts SET TripId = " + str(t_) + " WHERE GiftId IN(" + (",").join(map(str, g)) + ");")
            c.commit()

            trips = pd.read_sql(
                "SELECT * FROM (SELECT * FROM gifts WHERE TripId IS NULL ORDER BY i, j, Longitude, Latitude LIMIT " +
                str(limit_) + " ) ORDER BY Latitude DESC", c)
            # break

        print(c)
        ou_ = open("../submissions/12509884600.csv", "w")
        ou_.write("TripId,GiftId\n")
        bm = 0.0
        submission = pd.read_sql("SELECT TripId FROM gifts GROUP BY TripId ORDER BY TripId;", c)

        solution = {}
        for trip_ in submission.TripId:
            b = trip_
            trip = pd.read_sql("SELECT GiftId, Latitude, Longitude, Weight FROM gifts WHERE TripId = " +
                               str(trip_ + 1) + " ORDER BY Latitude DESC, Longitude ASC;", c)
            gifts = []
            # Put all gifts from trip in a
            for x_ in range(len(trip.GiftId)):
                gifts.append([trip.GiftId[x_], (trip.Latitude[x_], trip.Longitude[x_]), trip.Weight[x_]])
            solution[trip_] = bb_sort(gifts)

        print(solution)
        optimizedSolutions = []

        for i in range(10000):

            tripCounter = random.randint(2, len(submission.TripId))

            if 3 < tripCounter < len(submission.TripId) - 3 and tripCounter not in optimizedSolutions:
                print("TripCounter", tripCounter)
                tripCounter1 = tripCounter
                trip1 = pd.read_sql("SELECT GiftId, Latitude, Longitude, Weight FROM gifts WHERE TripId = " +
                                    str(submission.TripId[tripCounter1]) + " ORDER BY Latitude DESC, Longitude ASC;", c)

                giftOrderTrip1 = []

                # Put all gifts from trip in a
                for x_ in range(len(trip1.GiftId)):
                    giftOrderTrip1.append(
                        [trip1.GiftId[x_], (trip1.Latitude[x_], trip1.Longitude[x_]), trip1.Weight[x_]])
                # optimize a
                l1 = pathlength(giftOrderTrip1)
                optimizedGiftOrderTrip1 = optimizetrips(giftOrderTrip1)
                # optimizedGiftOrder = bb_sort(giftOrder)
                # Check if the new a is better or not
                l2 = pathlength(optimizedGiftOrderTrip1)
                # Not better
                if l1 <= l2:
                    print(submission.TripId[tripCounter1], "No Change")
                    # bm += pathlength(optimizedGiftOrderTrip1)

                    optimizedSolutions.append(tripCounter1)

                    # ou_.write(str(submission.TripId[tripCounter1])+","+str(optimizedGiftOrderTrip1[y_][0])+"\n")

                # Better: assign new benchmark value
                # Write new gifts to trips
                else:
                    print(submission.TripId[tripCounter1], "Optimized")
                    # bm += pathlength(optimizedGiftOrderTrip1)
                    solution[tripCounter1] = optimizedGiftOrderTrip1
                    if tripCounter1 in optimizedSolutions:
                        optimizedSolutions.remove(tripCounter1)
        for tripToWrite in solution:
            for y_ in range(len(solution[tripToWrite])):
                ou_.write(str(tripToWrite) + "," + str(solution[tripToWrite][y_][0]) + "\n")

        ou_.close()

        print("Previous Score: 12506717041.9")
        print("Submission score: ")
        print(n, limit_, bm)

        cu = c.cursor()
        cu.execute("UPDATE gifts SET TripId = NULL;")
        c.commit()
