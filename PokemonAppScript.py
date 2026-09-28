import requests
import customtkinter as ctk
from PIL import Image
import io

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class PokemonApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Pokemon App")
        self.attributes("-fullscreen", True)

        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.place(relx=0.5, rely=0.1, anchor="center")

        self.pokemon_name_entry = ctk.CTkEntry(
            self.nav_frame, placeholder_text="Enter Pokemon Name", width=250
        )
        self.pokemon_name_entry.pack(side="left", padx=10)

        self.search_button = ctk.CTkButton(
            self.nav_frame, text="Search", command=self.search_pokemon
        )
        self.search_button.pack(side="left", padx=10)

        self.results_frame = ctk.CTkScrollableFrame(
            self, width=1200, height=600, fg_color="transparent"
        )
        self.results_frame.pack(fill="x", expand=True, padx=10)

        self.displayed_cards = []

        self.status_label = ctk.CTkLabel(
            self, text="", font=("Arial", 14, "italic")
        )
        self.status_label.place(relx=0.5, rely=0.18, anchor="center")
        
        self.API_key = "Get your own API key from https://pokewallet.io/"
        self.headers = {"X-Api-Key": self.API_key} if self.API_key else {}

    def extract_prices(self, card):
        """Extracts prices directly from PokeWallet's list structure."""
        price_lines = []

        # 1. Check TCGPlayer prices (List of price dicts)
        tcg_data = card.get("tcgplayer")
        if isinstance(tcg_data, dict):
            prices_list = tcg_data.get("prices", [])
            if isinstance(prices_list, list):
                for price_entry in prices_list:
                    if isinstance(price_entry, dict):
                        sub_type = price_entry.get("sub_type_name", "Market")
                        # Try market_price, then mid_price, then low_price
                        market = (
                            price_entry.get("market_price") 
                            or price_entry.get("mid_price") 
                            or price_entry.get("low_price")
                        )
                        if isinstance(market, (int, float)):
                            price_lines.append(f"{sub_type}: ${market:.2f}")

        # 2. Check CardMarket prices if TCGPlayer returned nothing
        if not price_lines:
            cm_data = card.get("cardmarket")
            if isinstance(cm_data, dict):
                prices_list = cm_data.get("prices", [])
                if isinstance(prices_list, list):
                    for price_entry in prices_list:
                        if isinstance(price_entry, dict):
                            sub_type = price_entry.get("sub_type_name", "Avg")
                            market = (
                                price_entry.get("market_price") 
                                or price_entry.get("average_sell_price") 
                                or price_entry.get("trend_price")
                            )
                            if isinstance(market, (int, float)):
                                price_lines.append(f"CardMarket ({sub_type}): €{market:.2f}")

        return "\n".join(price_lines) if price_lines else "Price: N/A"

    def search_pokemon(self):
        pokemon_name = self.pokemon_name_entry.get().strip().lower()
        
        if not pokemon_name:
            return
            
        for card in self.displayed_cards:
            card.destroy()
        self.displayed_cards.clear()

        base_url = "https://api.pokewallet.io/search"
        query_parameters = {"q": pokemon_name}

        try:
            self.status_label.configure(text="Searching...")
            self.update()
            
            response = requests.get(base_url, headers=self.headers, params=query_parameters)

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                if isinstance(results, list) and len(results) > 0:
                    self.status_label.configure(text="")
                    self.display_pokemon_info(results)
                else:
                    self.status_label.configure(text="No matching card variants found.")
            else:
                self.status_label.configure(text=f"API Error. Status Code: {response.status_code}")
                
        except Exception as e:
            print(f"Network error details: {e}")
            self.status_label.configure(text="Network connection failure.")

    def display_pokemon_info(self, results_list):
        MAX_COLUMNS = 5

        for index, card in enumerate(results_list):
            try:
                if not isinstance(card, dict): 
                    continue

                card_info = card.get("card_info", {})
                if not isinstance(card_info, dict): 
                    card_info = {}
                
                name = card_info.get("name") or card_info.get("clean_name", "Unknown")
                rarity = card_info.get("rarity", "N/A")
                hp = card_info.get("hp", "N/A")
                if isinstance(hp, str) and hp.endswith(".0"):
                    hp = hp[:-2]  # Clean "200.0" -> "200"
                
                card_type = card_info.get("card_type", "N/A")
                
                # Extract prices using the updated method
                prices_text = self.extract_prices(card)

                row_num = index // MAX_COLUMNS
                col_num = index % MAX_COLUMNS

                card_box = ctk.CTkButton(
                    self.results_frame, width=300, height=250, 
                    fg_color="#3C3C3C", hover_color="#4A4A4A", 
                    command=lambda c=card: self.show_info(c)
                )
                card_box.grid(row=row_num, column=col_num, padx=15, pady=15)
                card_box.grid_propagate(False)

                self.displayed_cards.append(card_box)

                ctk.CTkLabel(card_box, text=name, font=("Arial", 14, "bold")).pack(pady=(10, 5))
                ctk.CTkLabel(card_box, text=f"Type: {card_type} | HP: {hp}").pack()
                ctk.CTkLabel(card_box, text=f"Rarity: {rarity}").pack()
                ctk.CTkLabel(card_box, text=prices_text, text_color="#4CAF50").pack(pady=10)

            except Exception as e:
                print(f"Skipped card due to parsing error: {e}")

    def show_info(self, card):
        self.results_frame.pack_forget()
        self.pokemon_name_entry.pack_forget()  
        self.search_button.pack_forget()

        if hasattr(self, 'info_frame'): 
            self.info_frame.destroy()
        if hasattr(self, 'detail_frame'): 
            self.detail_frame.destroy()

        self.info_frame = ctk.CTkFrame(self, width=1200, height=300)
        self.info_frame.pack(fill="both", expand=False, padx=10, pady=10)
        
        card_info = card.get("card_info", {})
        if not isinstance(card_info, dict): 
            card_info = {}
        
        name = card_info.get("name") or card_info.get("clean_name", "Unknown")
        self.name_label = ctk.CTkLabel(self.info_frame, text=name, font=("Arial", 40, "bold"))
        self.name_label.pack(pady=10)

        rarity = card_info.get("rarity", "N/A")
        card_type = card_info.get("card_type", "N/A")
        hp = card_info.get("hp", "N/A")
        if isinstance(hp, str) and hp.endswith(".0"):
            hp = hp[:-2]

        prices_text = self.extract_prices(card)

        info_text = f"Type: {card_type}\nHP: {hp}\nRarity: {rarity}\n\nMarket Prices:\n{prices_text}"
        
        self.other_info_label = ctk.CTkLabel(self.info_frame, text=info_text, font=("Arial", 18))
        self.other_info_label.pack(pady=5)

        card_id = card.get("id")
        image_url = f"https://api.pokewallet.io/images/{card_id}" if card_id else ""

        self.detail_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.detail_frame.pack(fill="both", expand=True, padx=20, pady=20)

        if image_url:
            try:
                img_headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(image_url, headers=self.headers if self.headers else img_headers)
                
                if response.status_code == 200:
                    image_data = Image.open(io.BytesIO(response.content))
                    card_image = ctk.CTkImage(light_image=image_data, size=(270, 377))
                    image_label = ctk.CTkLabel(self.detail_frame, image=card_image, text="")
                    image_label.pack(pady=10)
                else:
                    ctk.CTkLabel(self.detail_frame, text="Failed to load image").pack(pady=20)
                
            except Exception as e:
                ctk.CTkLabel(self.detail_frame, text="Failed to load image").pack(pady=20)
        else:
            ctk.CTkLabel(self.detail_frame, text="No image available for this card").pack(pady=20)

        back_btn = ctk.CTkButton(self.detail_frame, text="Back to Search", command=self.go_back)
        back_btn.pack(pady=20)

    def go_back(self):
        self.info_frame.pack_forget()
        self.detail_frame.pack_forget()
        self.results_frame.pack(fill="x", expand=True, padx=10)
        self.pokemon_name_entry.pack(side="left", padx=10)
        self.search_button.pack(side="left", padx=10)

if __name__ == "__main__":
    app = PokemonApp()
    app.mainloop()
