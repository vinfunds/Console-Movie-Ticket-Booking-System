import json
import os
from datetime import datetime

DATA_FILE = "cinema_data.json"

class Movie:
    def __init__(self, movie_id, title, duration_min, genre):
        self.movie_id = movie_id
        self.title = title
        self.duration_min = duration_min
        self.genre = genre

class Showtime:
    def __init__(self, showtime_id, movie_id, start_time, screen="Main"):
        self.showtime_id = showtime_id
        self.movie_id = movie_id
        self.start_time = start_time      # string "YYYY-MM-DD HH:MM"
        self.screen = screen
        self.seats = self._initialize_seats()

    def _initialize_seats(self):
        # 10 rows × 10 seats → A1–J10
        seats = {}
        for row in "ABCDEFGHIJ":
            for col in range(1, 11):
                seat_num = f"{row}{col}"
                seats[seat_num] = {"status": "available", "booking_id": None}
        return seats

class Booking:
    def __init__(self, booking_id, showtime_id, customer_name, seat_numbers):
        self.booking_id = booking_id
        self.showtime_id = showtime_id
        self.customer_name = customer_name
        self.seat_numbers = seat_numbers
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class CinemaManager:
    def __init__(self):
        self.movies = []
        self.showtimes = []
        self.bookings = []
        self.next_movie_id = 1
        self.next_showtime_id = 1
        self.next_booking_id = 10001
        self.load_data()

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            # Movies
            for m in data.get("movies", []):
                movie = Movie(m["movie_id"], m["title"], m["duration_min"], m["genre"])
                self.movies.append(movie)
                self.next_movie_id = max(self.next_movie_id, m["movie_id"] + 1)
            # Showtimes
            for s in data.get("showtimes", []):
                show = Showtime(s["showtime_id"], s["movie_id"], s["start_time"], s["screen"])
                show.seats = s["seats"]
                self.showtimes.append(show)
                self.next_showtime_id = max(self.next_showtime_id, s["showtime_id"] + 1)
            # Bookings
            for b in data.get("bookings", []):
                booking = Booking(b["booking_id"], b["showtime_id"], b["customer_name"], b["seat_numbers"])
                booking.timestamp = b["timestamp"]
                self.bookings.append(booking)
                self.next_booking_id = max(self.next_booking_id, b["booking_id"] + 1)
        except:
            print("Error loading data. Starting empty.")

    def save_data(self):
        data = {
            "movies": [vars(m) for m in self.movies],
            "showtimes": [{
                "showtime_id": s.showtime_id,
                "movie_id": s.movie_id,
                "start_time": s.start_time,
                "screen": s.screen,
                "seats": s.seats
            } for s in self.showtimes],
            "bookings": [vars(b) for b in self.bookings]
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def add_movie(self):
        title = input("Movie title: ").strip()
        duration = int(input("Duration (minutes): "))
        genre = input("Genre: ").strip()
        movie = Movie(self.next_movie_id, title, duration, genre)
        self.movies.append(movie)
        self.next_movie_id += 1
        print(f"Movie added → ID: {movie.movie_id}")

    def add_showtime(self):
        if not self.movies:
            print("No movies yet.")
            return
        self.display_movies()
        try:
            mid = int(input("Movie ID: "))
            movie = next((m for m in self.movies if m.movie_id == mid), None)
            if not movie:
                print("Movie not found.")
                return
            time_str = input("Showtime (YYYY-MM-DD HH:MM): ")
            show = Showtime(self.next_showtime_id, mid, time_str)
            self.showtimes.append(show)
            self.next_showtime_id += 1
            print(f"Showtime added → ID: {show.showtime_id}")
        except:
            print("Invalid input.")

    def display_movies(self):
        if not self.movies:
            print("No movies available.")
            return
        print("\nAvailable Movies:")
        for m in self.movies:
            print(f"  {m.movie_id:3d} | {m.title:30} | {m.genre:12} | {m.duration_min} min")

    def display_showtimes(self, movie_id=None):
        found = False
        print("\nShowtimes:")
        for s in self.showtimes:
            if movie_id is None or s.movie_id == movie_id:
                movie = next((m for m in self.movies if m.movie_id == s.movie_id), None)
                title = movie.title if movie else "???"
                print(f"  {s.showtime_id:3d} | {title:30} | {s.start_time} | Screen {s.screen}")
                found = True
        if not found:
            print("No showtimes found.")

    def display_seat_map(self, showtime_id):
        show = next((s for s in self.showtimes if s.showtime_id == showtime_id), None)
        if not show:
            print("Showtime not found.")
            return
        print(f"\nSeat Map – Showtime {showtime_id} ({show.start_time})")
        print("  " + " ".join(f"{col:2}" for col in range(1,11)))
        for row in "ABCDEFGHIJ":
            line = [row]
            for col in range(1,11):
                seat = f"{row}{col}"
                status = show.seats[seat]["status"]
                symbol = "██" if status == "booked" else "░░"
                line.append(symbol)
            print(" ".join(line))

    def book_seats(self):
        self.display_showtimes()
        try:
            sid = int(input("\nShowtime ID: "))
            show = next((s for s in self.showtimes if s.showtime_id == sid), None)
            if not show:
                print("Showtime not found.")
                return
            self.display_seat_map(sid)
            seats_str = input("Seats (comma separated e.g. A1,B2,C3): ")
            seat_list = [s.strip().upper() for s in seats_str.split(",")]
            customer = input("Your name: ").strip()

            for seat in seat_list:
                if seat not in show.seats:
                    print(f"Invalid seat: {seat}")
                    return
                if show.seats[seat]["status"] == "booked":
                    print(f"Seat {seat} already booked.")
                    return

            for seat in seat_list:
                show.seats[seat]["status"] = "booked"
                show.seats[seat]["booking_id"] = self.next_booking_id

            booking = Booking(self.next_booking_id, sid, customer, seat_list)
            self.bookings.append(booking)
            self.next_booking_id += 1
            print(f"\nBooking successful! Booking ID: {booking.booking_id}")
        except:
            print("Invalid input.")

    def cancel_booking(self):
        bid_str = input("Booking ID: ").strip()
        try:
            bid = int(bid_str)
            booking = next((b for b in self.bookings if b.booking_id == bid), None)
            if not booking:
                print("Booking not found.")
                return
            show = next((s for s in self.showtimes if s.showtime_id == booking.showtime_id), None)
            if show:
                for seat in booking.seat_numbers:
                    show.seats[seat]["status"] = "available"
                    show.seats[seat]["booking_id"] = None
            self.bookings = [b for b in self.bookings if b.booking_id != bid]
            print(f"Booking {bid} cancelled successfully.")
        except:
            print("Invalid booking ID.")

    def view_all_bookings(self):
        if not self.bookings:
            print("No bookings yet.")
            return
        print("\nAll Bookings:")
        for b in self.bookings:
            show = next((s for s in self.showtimes if s.showtime_id == b.showtime_id), None)
            title = next((m.title for m in self.movies if m.movie_id == show.movie_id), "?") if show else "?"
            print(f"  {b.booking_id} | {b.customer_name:20} | {title:25} | {b.timestamp} | Seats: {', '.join(b.seat_numbers)}")

def display_menu():
    print("\n" + "═"*60)
    print("          CINEMA TICKET BOOKING SYSTEM")
    print("═"*60)
    print(" 1. Add movie")
    print(" 2. Add showtime")
    print(" 3. View movies")
    print(" 4. View showtimes")
    print(" 5. View seat map")
    print(" 6. Book seats")
    print(" 7. Cancel booking")
    print(" 8. View all bookings (admin)")
    print(" 9. Exit & Save")
    print("═"*60)

def main():
    manager = CinemaManager()
    while True:
        display_menu()
        choice = input("→ ").strip()
        if choice == "1":
            manager.add_movie()
        elif choice == "2":
            manager.add_showtime()
        elif choice == "3":
            manager.display_movies()
        elif choice == "4":
            manager.display_showtimes()
        elif choice == "5":
            try:
                sid = int(input("Showtime ID: "))
                manager.display_seat_map(sid)
            except:
                print("Invalid ID.")
        elif choice == "6":
            manager.book_seats()
        elif choice == "7":
            manager.cancel_booking()
        elif choice == "8":
            manager.view_all_bookings()
        elif choice == "9":
            manager.save_data()
            print("Data saved. Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()