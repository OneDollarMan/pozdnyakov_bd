from mysql.connector import connect, Error


class CleaningRepo:
    ROLE_INSPECTOR = 1
    ROLE_CLEANER = 2
    ROLE_SUPERVISOR = 3

    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = "gmfk2ASD"
        self.database = "cleaning"
        self.connection = self.get_connect()
        self.cursor = self.connection.cursor()

        self.get_tables = lambda: self.raw_query("SHOW TABLES")

        self.get_user = lambda username: self.raw_query("SELECT * FROM user WHERE username='%s'" % username)
        self.get_user_by_id = lambda id: self.get_query("SELECT * FROM user u JOIN role r ON u.role_id=r.id, u.id='%d'" % id)
        self.login_user = lambda username, password: self.get_query("SELECT * FROM user WHERE username='%s' AND password='%s'" % (username, password))
        self.add_user = lambda u, p, f, r: self.write_query("INSERT INTO user SET username='%s', password='%s', fio='%s', role_id='%d'" % (u, p, f, r))
        self.get_users = lambda: self.raw_query("SELECT * FROM user JOIN role ON user.role_id=role.id")
        self.get_roles = lambda: self.raw_query("SELECT * FROM role")
        self.rm_user = lambda id: self.write_query("DELETE FROM user WHERE id='%d'" % id)

        self.get_clients = lambda: self.raw_query("SELECT * FROM client WHERE hidden='0'")
        self.add_client = lambda fio, n, a: self.write_query("INSERT INTO client SET fio='%s', number='%s', address='%s'" % (fio, n, a))
        self.rm_client = lambda id: self.write_query("UPDATE client SET hidden='1' WHERE id='%d'" % id)

        self.get_orders = lambda: self.raw_query("SELECT * FROM cleaning.order o JOIN client c, thing_type t, cleaning_type cl, status s WHERE o.client_id=c.id AND o.type_id=t.id AND o.cleaning_id=cl.id AND o.status_id=s.id ORDER BY date ASC")
        self.add_order = lambda c, t, n, cl: self.write_query("INSERT INTO cleaning.order SET `client_id`='%d', `type_id`='%d', `name`='%s', `cleaning_id`='%d'" % (c, t, n , cl))
        self.rm_order = lambda id: self.write_query("DELETE FROM cleaning.order WHERE id='%d'" % id)
        self.change_order_status = lambda id, s: self.write_query("UPDATE cleaning.order SET status_id='%d' WHERE id='%d'" % (s, id))
        self.get_stats = lambda: self.raw_query("SELECT DATE_FORMAT(date, '%d-%m-%Y'), COUNT(*), SUM(price) FROM cleaning.order JOIN cleaning_type c ON cleaning_id=c.id GROUP BY DATE_FORMAT(date, '%d-%m-%Y')")

        self.get_types = lambda: self.raw_query("SELECT * FROM thing_type WHERE hidden=0")
        self.add_type = lambda n: self.write_query("INSERT INTO thing_type SET name='%s'" % n)
        self.rm_type = lambda id: self.write_query("UPDATE thing_type SET hidden=1 WHERE id='%d'" % id)

        self.get_cleanings = lambda: self.raw_query("SELECT * FROM cleaning_type WHERE hidden=0")
        self.add_cleaning = lambda n, p: self.write_query("INSERT INTO cleaning_type SET name='%s', price='%d'" % (n, p))
        self.rm_cleaning = lambda id: self.write_query("UPDATE cleaning_type SET hidden=1 WHERE id='%d'" % id)

        self.get_statuses = lambda: self.raw_query("SELECT * FROM status")

    def get_connect(self):
        try:
            return connect(host=self.host, user=self.user, password=self.password, database=self.database)
        except Error as e:
            print(e)

    def raw_query(self, query):
        if self.cursor and query:
            self.cursor.execute(query)
            return self.cursor.fetchall()

    def write_query(self, query):
        if self.cursor and query:
            self.cursor.execute(query)
            self.connection.commit()
            return self.cursor.fetchall()

    def get_query(self, query):
        if self.cursor and query:
            self.cursor.execute(query)
            return self.cursor.fetchone()

    def reg_user(self, u, p, f, r):
        if not self.get_user(u):
            self.add_user(u, p, f, r)
            return True
        else:
            return False
