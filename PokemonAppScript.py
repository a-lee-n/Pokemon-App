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

    def search_pokemon(self):
        pokemon_name = self.pokemon_name_entry.get().strip().lower()
        
        if not pokemon_name:
            return
            
        for card in self.displayed_cards:
            card.destroy()
        self.displayed_cards.clear()

        API_key = "Go get you own API key from https://docs.pokemontcg.io/ and then replace this string with your own key"
        base_url = "https://api.pokemontcg.io/v2/cards"
        headers = {"X-Api-Key": API_key}
        
        query_parameters = {"q": f'name:"{pokemon_name}"'}

        try:
            response = requests.get(base_url, headers=headers, params=query_parameters)

            if response.status_code == 200:
                data = response.json()
                if data.get("data"):
                    self.status_label.configure(text="")
                    self.display_pokemon_info(data)
                else:
                    self.status_label.configure(
                        text="No matching card variants found."
                    )
            else:
                self.status_label.configure(
                    text=f"API Error. Status Code: {response.status_code}"
                )
        except Exception as e:
            self.status_label.configure(text="Network connection failure.")

    def display_pokemon_info(self, data):
        MAX_COLUMNS = 7

        for index, card in enumerate(data["data"]):
            name = card.get("name", "Unknown")
            rarity = card.get("rarity", "N/A")
            hp = card.get("hp", "N/A")

            types_list = card.get("types", ["N/A"])
            card_type = types_list[0] if types_list else "N/A"

            tcg_prices = card.get("tcgplayer", {}).get("prices", {})
            price_lines = []
            
            if "normal" in tcg_prices and "market" in tcg_prices["normal"]:
                price_lines.append(f"Normal: ${tcg_prices['normal']['market']:.2f}")
                
            if "holofoil" in tcg_prices and "market" in tcg_prices["holofoil"]:
                price_lines.append(f"Holo: ${tcg_prices['holofoil']['market']:.2f}")
                
            if "reverseHolofoil" in tcg_prices and "market" in tcg_prices["reverseHolofoil"]:
                price_lines.append(f"Reverse: ${tcg_prices['reverseHolofoil']['market']:.2f}")

            prices_text = "\n".join(price_lines) if price_lines else "Price: N/A"

            row_num = index // MAX_COLUMNS
            col_num = index % MAX_COLUMNS

            card_box = ctk.CTkButton(self.results_frame, width=300, height=250, fg_color="#3C3C3C", hover_color="#4A4A4A", command= lambda c=card: self.show_info(c))
            card_box.grid(row=row_num, column=col_num, padx=15, pady=15)
            card_box.grid_propagate(False)

            self.displayed_cards.append(card_box)

            ctk.CTkLabel(
                card_box, text=name, font=("Arial", 14, "bold")
            ).pack(pady=(10, 5))
            ctk.CTkLabel(
                card_box, text=f"Type: {card_type} | HP: {hp}"
            ).pack()
            ctk.CTkLabel(card_box, text=f"Rarity: {rarity}").pack()
            ctk.CTkLabel(
                card_box, text=prices_text, text_color="#4CAF50"
            ).pack(pady=10)

    def show_info(self, card):
        self.results_frame.pack_forget()
        self.pokemon_name_entry.pack_forget()    
        self.search_button.pack_forget()

        self.info_frame = ctk.CTkFrame(self, width=1200, height=600)
        self.info_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.name_label = ctk.CTkLabel(self.info_frame, text=card.get("name", "Unknown"), font=("Arial", 60, "bold"))
        self.name_label.pack(pady=10)

        rarity = card.get("rarity", "N/A")
        card_type = card.get("types", ["N/A"])[0] if card.get("types") else "N/A"
        hp = card.get("hp", "N/A")

        tcg_prices = card.get("tcgplayer", {}).get("prices", {})
        price_lines = []
        
        if "normal" in tcg_prices and "market" in tcg_prices["normal"]:
            price_lines.append(f"Normal: ${tcg_prices['normal']['market']:.2f}")
            
        if "holofoil" in tcg_prices and "market" in tcg_prices["holofoil"]:
            price_lines.append(f"Holo: ${tcg_prices['holofoil']['market']:.2f}")
            
        if "reverseHolofoil" in tcg_prices and "market" in tcg_prices["reverseHolofoil"]:
            price_lines.append(f"Reverse: ${tcg_prices['reverseHolofoil']['market']:.2f}")

        prices_text = "\n".join(price_lines) if price_lines else "Price: N/A"

        info_text = f"Type: {card_type}\nHP: {hp}\nRarity: {rarity}\n\nMarket Prices:\n{prices_text}"
        
        self.other_info_label = ctk.CTkLabel(self.info_frame, text=info_text, font=("Arial", 20))
        self.other_info_label.pack(pady=5)

        images_info = card.get("images", {})
        image_url = images_info.get("large", "")

        self.detail_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.detail_frame.pack(fill="both", expand=True, padx=20, pady=20)

        if image_url:
            try:
                response = requests.get(image_url)
                image_data = Image.open(io.BytesIO(response.content))
                card_image = ctk.CTkImage(light_image=image_data, size=(367, 512))
                image_label = ctk.CTkLabel(self.detail_frame, image=card_image, text="")
                image_label.pack(pady=20)
                
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
