from flask import Flask, render_template, request
from datetime import date
from better_profanity import profanity
from langdetect import detect
import pymysql

app = Flask(__name__)
given_crn = "dummy"
given_user = "dummy"


class Database:
    def __init__(self):
        host = "localhost"
        user = "root"
        password = "S3RCS411"
        db = "Insightify"
        self.con = pymysql.connect(host=host, user=user, password=password, db=db,
                                   cursorclass=pymysql.cursors.DictCursor)
        self.cur = self.con.cursor()

    def disconnect(self):
        self.cur.close()
        self.con.close()

    def stored_proc(self):
        self.cur.callproc('sp2', [given_crn])

    def get_sp_res(self):
        self.cur.execute("select * from NewTable")
        result = self.cur.fetchall()
        return result

    def get_sp2_res(self):
        self.cur.execute("select * from NewTable1")
        result = self.cur.fetchall()
        return result


    # advance query 1 - READ
    def get_course_info(self, given_crn):
        self.cur.execute("SELECT CS.CRN, CS.YearTerm, I.Instructor_name, I.ID, AVG(E.Score)as avg_score, "
                         "AVG(Reviews.WorkLoad) as avg_load, AVG(Reviews.Difficulty) as avg_diff, AVG(Reviews.Rating) "
                         "as avg_rating, count(DISTINCT Reviews.ReviewId) as num_revs, count(DISTINCT E.NetId) as "
                         "enrollments FROM CourseSchedule CS JOIN "
                         "Instructors I on (CS.instructor_id=I.ID) Join "
                         "Enrollments E on (CS.CRN=E.CRN and CS.YearTerm=E.Term) JOIN Reviews on CS.CRN=Reviews.CRN "
                         "and CS.YearTerm=Reviews.Term "
                         "WHERE CS.CRN = %s  GROUP BY CS.YearTerm,I.Instructor_name,I.ID;", str(given_crn))
        result = self.cur.fetchall()
        return result

    # advance query 2
    def get_instructor_course_info(self, given_ins_id):
        self.cur.execute(
            "SELECT Grade, COUNT(*) as count_grade FROM CourseSchedule CS Join Enrollments E on (CS.CRN=E.CRN and "
            "CS.YearTerm=E.Term) WHERE CS.CRN = \'%s\' and CS.instructor_id = \'%s\' GROUP BY Grade ORDER BY Grade "
            % (
            str(given_crn), str(given_ins_id)))
        result = self.cur.fetchall()
        return result

    # TermTrigger1
    def create_trigger(self):
        self.cur.execute(" drop trigger if exists TermTrigger1")
        triggerstr = "CREATE TRIGGER TermTrigger1 \
                       AFTER INSERT ON Reviews \
                       FOR EACH ROW \
                       BEGIN \
                       SET @term = (SELECT YearTerm FROM CourseSchedule where CRN = new.CRN AND YearTerm = new.Term); \
                       IF @term IS NULL THEN INSERT INTO CourseSchedule VALUES(new.CRN,new.Term,1234); \
                       END IF; \
                       END"
        self.cur.execute(triggerstr)
        self.con.commit()

    # TermTrigger2
    def create_trigger2(self):
        self.cur.execute(" drop trigger if exists TermTrigger2")
        triggerstr = "CREATE TRIGGER TermTrigger2 \
                       BEFORE UPDATE ON Reviews \
                       FOR EACH ROW \
                       BEGIN \
                       SET @term = (SELECT YearTerm FROM CourseSchedule where CRN = new.CRN AND YearTerm = new.Term); \
                       IF @term IS NULL THEN INSERT INTO CourseSchedule VALUES(new.CRN,new.Term,1234); \
                       END IF; \
                       END"
        self.cur.execute(triggerstr)
        self.con.commit()

    # WorkLoadTrigger1
    def create_trigger3(self):
        self.cur.execute(" drop trigger if exists WorkLoadTrigger1")
        # triggerstr = "CREATE TRIGGER TermTrigger BEFORE UPDATE ON Reviews FOR EACH ROW BEGIN INSERT INTO CourseSchedule VALUES(new.CRN,new.CRN,NULL); END"
        triggerstr = "CREATE TRIGGER WorkLoadTrigger1 \
                    BEFORE INSERT ON Reviews \
                    FOR EACH ROW BEGIN \
                    IF (new.WorkLoad < 4) THEN\
                    SET new.WorkLoad = 1; \
                    ELSEIF (new.WorkLoad >=4 AND new.WorkLoad < 8) THEN \
                    SET new.WorkLoad = 2; \
                    ELSEIF (new.WorkLoad >=8 AND new.WorkLoad < 12) THEN \
                    SET new.WorkLoad = 3; \
                    ELSEIF (new.WorkLoad >=12 AND new.WorkLoad < 16) THEN \
                    SET new.WorkLoad = 4; \
                    ELSEIF (new.WorkLoad >= 16) THEN \
                    SET new.WorkLoad = 5; \
                    END IF; \
                    END"
        self.cur.execute(triggerstr)
        self.con.commit()

    # WorkLoadTrigger2
    def create_trigger4(self):
        self.cur.execute(" drop trigger if exists WorkLoadTrigger2")
        # triggerstr = "CREATE TRIGGER TermTrigger BEFORE UPDATE ON Reviews FOR EACH ROW BEGIN INSERT INTO CourseSchedule VALUES(new.CRN,new.CRN,NULL); END"
        triggerstr = "CREATE TRIGGER WorkLoadTrigger2 \
                    BEFORE UPDATE ON Reviews \
                    FOR EACH ROW BEGIN \
                    IF (new.WorkLoad < 4) THEN\
                    SET new.WorkLoad = 1; \
                    ELSEIF (new.WorkLoad >=4 AND new.WorkLoad < 8) THEN \
                    SET new.WorkLoad = 2; \
                    ELSEIF (new.WorkLoad >=8 AND new.WorkLoad < 12) THEN \
                    SET new.WorkLoad = 3; \
                    ELSEIF (new.WorkLoad >=12 AND new.WorkLoad < 16) THEN \
                    SET new.WorkLoad = 4; \
                    ELSEIF (new.WorkLoad >= 16) THEN \
                    SET new.WorkLoad = 5; \
                    END IF; \
                    END"
        self.cur.execute(triggerstr)
        self.con.commit()

    # # trigger
    # def create_trigger(self):
    #     self.cur.execute(" drop trigger if exists TermTrigger")
    #     triggerstr = "CREATE TRIGGER TermTrigger \
    #                    BEFORE INSERT ON Reviews \
    #                    FOR EACH ROW \
    #                    BEGIN \
    #                    SET @term = (SELECT YearTerm FROM CourseSchedule where CRN = new.CRN AND YearTerm = new.Term); \
    #                    IF @term IS NULL THEN INSERT INTO CourseSchedule VALUES(new.CRN,new.Term,1234); \
    #                    END IF; \
    #                    END"
    #     self.cur.execute(triggerstr)
    #     self.con.commit()

    # get reviews for a given crn
    def get_course_reviews(self, given_crn):
        self.cur.execute("SELECT * FROM Reviews WHERE CRN = %s LIMIT 100", str(given_crn))
        result = self.cur.fetchall()
        return result

    # get reviews for a given crn and term
    def get_course_reviews_per_term(self, crn, term):
        self.cur.execute("SELECT * FROM Reviews WHERE CRN = \'%s\' and Term = \'%s\' LIMIT 100" % (str(crn), str(term)))
        result = self.cur.fetchall()
        return result

    # get sub-reviews for a given reviewId
    def get_sub_reviews(self, review_id):
        self.cur.execute("select * from SubReviews join Assessments on "
                         "SubReviews.AssessmentId=Assessments.AssessmentId WHERE ReviewId = %s LIMIT 100",
                         str(review_id))
        result = self.cur.fetchall()
        return result

    # get reviews for a given NetId
    def get_reviews(self):
        self.cur.execute("SELECT * FROM Reviews WHERE NetId = %s", str(given_user))
        result = self.cur.fetchall()
        return result

    # delete a review for a given review id
    def delete_Review(self, rev_id):
        self.cur.execute("DELETE FROM Reviews WHERE ReviewId = %s", str(rev_id))
        self.con.commit()
        return True

    # update a review
    def update_Review(self, given_rev_id, given_course, given_term, given_wl, given_diff, given_rating, given_rev):
        self.cur.execute(
            "UPDATE Reviews SET CRN=\'%s\', WorkLoad=\'%s\', Difficulty=\'%s\', Rating=\'%s\', TextReview=\'%s\', "
            "Date=\'%s\', Term=\'%s\' WHERE ReviewId =\'%s\'" % (
            str(given_course), str(given_wl), str(given_diff), str(given_rating), str(given_rev), date.today(),
            str(given_term), str(given_rev_id)))
        self.con.commit()
        return True

    #insert a sub review
    def insert_sub_review(self,given_subreview_id, review_id,asses_id, given_wl, given_diff, given_rating, given_rev):
        self.cur.execute(
            "INSERT INTO SubReviews VALUES(\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')" % (
            str(given_subreview_id), str(review_id), str(asses_id), str(given_wl), str(given_diff), str(given_rating),
            str(given_rev))
        )
        self.con.commit()
        return True

    # get last review id to add a new review
    def getMaxReviewId(self):
        self.cur.execute("select max(ReviewId) from Reviews")
        result = self.cur.fetchall()
        return result

    # get last sub review id to add a new subreview
    def getMaxSubReviewId(self):
        self.cur.execute("select max(SubReviewId) from SubReviews")
        result = self.cur.fetchall()
        return result

    # get assess_id
    def get_assess_id(self, review_id):
        self.cur.execute(
            "select min(AssessmentId) from Assessments A join Reviews R on A.CRN=R.CRN where R.ReviewId=%s",
            str(review_id))
        result = self.cur.fetchall()
        # print(result[0]['min(AssessmentId)'])
        return result[0]['min(AssessmentId)']

    # insert a new review
    def insert_review(self, given_rev_id, given_course, given_term, given_wl, given_diff, given_rating, given_rev):
        # print(given_term)
        self.cur.execute(
            "INSERT INTO Reviews VALUES(\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')" % (
            str(given_rev_id), str(given_user), str(given_course), str(given_wl), str(given_diff), str(given_rating),
            str(given_rev), date.today(), str(given_term)))
        self.con.commit()
        return True

    # get review for a given review id
    def get_Review(self, rev_id):
        self.cur.execute("SELECT * FROM Reviews WHERE ReviewId = %s", str(rev_id))
        result = self.cur.fetchall()
        return result

    # check password
    def check_password(self, given_user, given_password):
        self.cur.execute("SELECT * FROM User WHERE UserId = %s", str(given_user))
        result = self.cur.fetchall()
        correct_password = result[0]['Password']
        if given_password == correct_password:
            return True
        else:
            return False

    # insert a new user - sign up
    def insert_user(self, given_user, given_password, given_role, given_fname, given_lname, given_dept):
        self.cur.execute(
            "INSERT INTO User VALUES(\'%s\',\'%s\',\'%s\')" % (str(given_user), str(given_password), str(given_role)))
        self.con.commit()
        result = self.cur.fetchall()
        self.cur.execute(
            "INSERT INTO Students VALUES(\'%s\',\'%s\',\'%s\',\'%s\')" % (str(given_fname), str(given_lname), str(given_user), str(given_dept)))
        self.con.commit()
        result2 = self.cur.fetchall()
        return result, result2


@app.route('/', methods=["post", "get"])
def firstpage():
    return render_template("index.html")


@app.route('/homepage', methods=["post", "get"])
def homepage():
    return firstpage()


@app.route('/loginPage', methods=["post", "get"])
def loginPage():
    return render_template("login.html")


@app.route('/user', methods=["post", "get"])
def user():
    global given_user
    if given_user != "dummy":
        return render_template("index2.html", result=given_user)
    db = Database()
    given_user = request.form["netid"]
    given_password = request.form["pwd"]
    password_check = db.check_password(given_user, given_password)
    db.disconnect()
    if password_check:
        return render_template("index2.html", result=given_user)
    else:
        return render_template("failed_login.html")


# @app.route('/course', methods=["post", "get"])
# def course():
#     global given_crn
#     given_crn = request.form["Course"]
#     db = Database()
#     res = db.get_course_info(given_crn)
#     db.disconnect()
#     return render_template("course_list.html", crn=given_crn, result=res)

@app.route('/course', methods=["post", "get"])
def course():
    global given_crn
    given_crn = request.form["Course"]
    db = Database()
    db.stored_proc()
    res = db.get_sp_res()
    res2 = db.get_sp2_res()
    db.disconnect()
    return render_template("course_list.html", crn=given_crn, result=res, result2=res2)


@app.route('/instructor/<given_ins_id>', methods=["post", "get"])
def instructor(given_ins_id=None):
    db = Database()
    res = db.get_instructor_course_info(given_ins_id)
    db.disconnect()
    return render_template("instructor.html", result=res)


@app.route('/coursereviews', methods=["post", "get"])
def coursereviews():
    global given_crn
    # given_crn = request.form["Course"]
    db = Database()
    res = db.get_course_reviews(given_crn)
    db.disconnect()
    return render_template("course_reviews.html", result=res)


@app.route('/reviewsCrnTerm/<crn>/<term>', methods=["post", "get"])
def getReviewsPerCRNTerm(crn, term):
    # global given_crn
    # given_crn = request.form["Course"]
    db = Database()
    res = db.get_course_reviews_per_term(crn, term)
    db.disconnect()
    return render_template("course_reviews.html", result=res)


@app.route('/subreviews/<review_id>', methods=["post", "get"])
def subreviews(review_id):
    db = Database()
    res = db.get_sub_reviews(review_id)
    db.disconnect()
    return render_template("sub_reviews.html", review_id = review_id, result=res)


@app.route('/addSubReviewPage/<review_id>', methods=["post", "get"])
def addSubReviewPage(review_id):
    return render_template("subreview.html",review_id=review_id)


@app.route('/createSubReview/<review_id>', methods=["post", "get"])
def createSubReview(review_id):
    given_type = request.form["group0"]
    given_wl = request.form["group1"]
    given_diff = request.form["group2"]
    given_rating = request.form["group3"]
    given_rev = request.form["subreview"]

    db = Database()
    maxCount = db.getMaxSubReviewId()

    given_subreview_id = int(maxCount[0]['max(SubReviewId)']) + 1
    asses_id = db.get_assess_id(review_id)
    db.insert_sub_review(given_subreview_id, review_id, asses_id, given_wl, given_diff, given_rating, given_rev)
    db.disconnect()
    return subreviews(review_id)


@app.route('/signupPage', methods=["post", "get"])
def signupPage():
    return render_template("signup.html")


@app.route('/signupSuccessful', methods=["post", "get"])
def signupSuccessful():
    db = Database()
    given_user = request.form["netid"]
    given_password = request.form["pwd"]
    given_role = request.form["role"]
    given_fname = request.form["FirstName"]
    given_lname = request.form["LastName"]
    given_dept = request.form["DeptID"]

    db.insert_user(given_user, given_password, given_role, given_fname, given_lname, given_dept)
    db.disconnect()
    return render_template("login.html")


@app.route('/reviews', methods=["post", "get"])
def reviews():
    global given_user
    db = Database()
    # db.create_trigger()
    db.create_trigger()
    db.create_trigger2()
    db.create_trigger3()
    db.create_trigger4()
    res = db.get_reviews()
    db.disconnect()
    return render_template("reviews.html", user=given_user, result=res)


@app.route('/deleteReview/<rev_id>', methods=["post", "get"])
def deleteReview(rev_id):
    global given_user
    db = Database()
    db.delete_Review(rev_id)
    res = db.get_reviews()
    db.disconnect()
    return render_template("reviews.html", user=given_user, result=res)


@app.route('/updateReviewPage/<rev_id>', methods=["post", "get"])
def updateReviewPage(rev_id):
    db = Database()
    review = db.get_Review(rev_id)
    db.disconnect()
    return render_template("updatereviewpage.html", review=review, result=rev_id)


@app.route('/updateReview/<rev_id>', methods=["post", "get"])
def updateReview(rev_id):
    global given_user
    given_course = request.form["Course"]
    given_term = request.form["Term"]
    given_wl = request.form["WorkLoad"]
    given_diff = request.form["group2"]
    given_rating = request.form["group3"]
    given_rev = request.form["review"]

    db = Database()
    # given_rev_id, given_course, given_term, given_wl, given_diff, given_rating, given_rev
    db.update_Review(rev_id, given_course, given_term, given_wl, given_diff, given_rating, given_rev)
    res = db.get_reviews()
    db.disconnect()
    return render_template("reviews.html", user=given_user, result=res)


@app.route('/addReviewPage', methods=["post", "get"])
def addReviewPage():
    return render_template("review.html")


@app.route('/createReview', methods=["post", "get"])
def createReview():
    global given_user
    given_course = request.form["Course"]
    given_term = request.form["Term"]
    given_wl = request.form["WorkLoad"]
    given_diff = request.form["group2"]
    given_rating = request.form["group3"]
    given_rev = request.form["review"]

    a = profanity.contains_profanity(given_rev)
    b = detect(given_rev)

    if a:
        res = "Review Discarded Due to Profanity"
        return render_template("failed_review.html", result=res)
    elif b != 'en':
        res = "Gibberish Review"
        return render_template("failed_review.html", result=res)

    db = Database()
    maxCount = db.getMaxReviewId()

    given_rev_id = int(maxCount[0]['max(ReviewId)']) + 1
    db.insert_review(given_rev_id, given_course, given_term, given_wl, given_diff, given_rating, given_rev)
    res = db.get_reviews()
    db.disconnect()
    return render_template("reviews.html", user=given_user, result=res)


if __name__ == "__main__":
    app.run(debug=True)
