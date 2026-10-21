import customtkinter as ctk


class EpisodesPanel(ctk.CTkFrame):
    def __init__(self, parent, selection_callback=None):
        super().__init__(parent, fg_color="transparent")

        self.episodes = []
        self.season_widgets = {}  
        self.selection_callback = selection_callback
        self._updating_selection = False 

        self.create_widgets()

    def create_widgets(self):
        top = ctk.CTkFrame(self, fg_color="transparent")

        top.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(
            top,
            text="☑ Выделить всё",
            height=35,
            corner_radius=12,
            command=self.select_all,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            top,
            text="☐ Убрать всё",
            height=35,
            corner_radius=12,
            fg_color="#3a3f4b",
            hover_color="#505766",
            command=self.clear_all,
        ).pack(side="left", padx=5)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="#10141f", corner_radius=15)

        self.scroll.pack(fill="both", expand=True)

    def set_episodes(self, episodes, group_by_season=False):
        self.episodes = episodes

        for widget in self.scroll.winfo_children():
            widget.destroy()

        self.season_widgets.clear()

        if not group_by_season:
            # Original flat list behavior
            self._create_flat_list(episodes)
        else:
            # New seasonal grouping behavior
            self._create_seasonal_groups(episodes)

    def _create_flat_list(self, episodes):
        """Create the original flat list of episodes"""
        self.checkboxes = []

        for item in episodes:
            season = item.get("season")
            episode = item.get("episode")

            if season and episode:
                text = f"{season} сезон {episode} серия | {item.get('episode_title') or item.get('show_name')}"
            else:
                text = f"🎬 {item['title']}"

            checkbox = ctk.CTkCheckBox(
                self.scroll,
                text=text,
                corner_radius=6,
                fg_color="#5865F2",
                hover_color="#4752C4",
                command=self.selection_changed,
            )

            checkbox.pack(fill="x", padx=10, pady=5)

            self.checkboxes.append(checkbox)
            checkbox.select()

    def _create_seasonal_groups(self, episodes):
        """Create seasonal grouped tree structure"""
        # Group episodes by season
        seasons_dict = {}
        no_season_episodes = []

        for idx, item in enumerate(episodes):
            season = item.get("season")
            episode = item.get("episode")
            
            if season is not None and episode is not None:
                # Convert to int for sorting if possible
                try:
                    season_key = int(season)
                except (ValueError, TypeError):
                    season_key = str(season)
                
                if season_key not in seasons_dict:
                    seasons_dict[season_key] = []
                seasons_dict[season_key].append((idx, item))
            else:
                no_season_episodes.append((idx, item))

        # Sort seasons numerically
        def season_sort_key(x):
            try:
                return int(x)
            except (ValueError, TypeError):
                return float('inf')

        sorted_seasons = sorted(seasons_dict.keys(), key=season_sort_key)

        # Create widgets for each season
        for season_key in sorted_seasons:
            season_episodes = seasons_dict[season_key]
            # Sort episodes within season
            season_episodes.sort(key=lambda x: self._episode_sort_key(x[1].get("episode")))
            
            season_num = season_episodes[0][1].get("season")
            self._create_season_group(season_num, season_episodes)

        # Handle episodes without season (if any)
        if no_season_episodes:
            no_season_episodes.sort(key=lambda x: self._episode_sort_key(x[1].get("episode")))
            self._create_season_group("Без сезона", no_season_episodes)

        # Initially select all
        self.select_all()

    def _episode_sort_key(self, episode):
        """Sort key for episodes - handles both int and string"""
        try:
            return int(episode)
        except (ValueError, TypeError):
            return float('inf')

    def _create_season_group(self, season_name, season_episodes):
        """Create a season group with header, checkbox, expand button, and episodes container"""
        total_episodes = len(season_episodes)
        
        # Main container for this season
        season_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        season_frame.pack(fill="x", padx=5, pady=2)

        # Header frame with checkbox, expand button, season name, and counter
        header_frame = ctk.CTkFrame(season_frame, fg_color="#1a1f2e", corner_radius=8)
        header_frame.pack(fill="x", pady=(0, 2))

        # Season checkbox
        season_checkbox = ctk.CTkCheckBox(
            header_frame,
            text="",
            width=24,
            height=24,
            corner_radius=4,
            fg_color="#5865F2",
            hover_color="#4752C4",
            command=lambda s=season_name: self._on_season_checkbox_click(s),
        )
        season_checkbox.pack(side="left", padx=(10, 5), pady=8)

        # Expand/collapse button
        expand_btn = ctk.CTkButton(
            header_frame,
            text="▼",
            width=28,
            height=28,
            corner_radius=4,
            fg_color="transparent",
            hover_color="#2a2f3e",
            font=("Segoe UI", 10),
            command=lambda s=season_name: self._toggle_season(s),
        )
        expand_btn.pack(side="left", padx=2, pady=8)

        # Season label with counter
        counter_text = f"{season_name} сезон ({total_episodes}/{total_episodes})" if isinstance(season_name, (int, str)) and str(season_name).isdigit() else f"{season_name} ({total_episodes}/{total_episodes})"
        season_label = ctk.CTkLabel(
            header_frame,
            text=counter_text,
            font=("Segoe UI", 13, "bold"),
            text_color="#ffffff",
        )
        season_label.pack(side="left", padx=8, pady=8)

        # Episodes container (initially visible)
        episodes_container = ctk.CTkFrame(season_frame, fg_color="transparent")
        episodes_container.pack(fill="x", padx=(30, 0))

        # Create episode checkboxes
        episode_checkboxes = []
        for original_idx, item in season_episodes:
            episode = item.get("episode")
            episode_title = item.get("episode_title") or ""
            
            text = f"{season_name} сезон {episode} серия"
            if episode_title:
                text += f" | {episode_title}"

            checkbox = ctk.CTkCheckBox(
                episodes_container,
                text=text,
                corner_radius=6,
                fg_color="#5865F2",
                hover_color="#4752C4",
                command=lambda idx=original_idx: self._on_episode_checkbox_click(idx),
            )

            checkbox.pack(fill="x", padx=10, pady=3)
            checkbox.select()  # Initially select all
            
            episode_checkboxes.append({
                'checkbox': checkbox,
                'index': original_idx,
                'episode': episode,
            })

        # Store season widget references
        self.season_widgets[season_name] = {
            'header_frame': header_frame,
            'season_checkbox': season_checkbox,
            'expand_btn': expand_btn,
            'season_label': season_label,
            'episodes_container': episodes_container,
            'episode_checkboxes': episode_checkboxes,
            'expanded': True,
            'total_episodes': total_episodes,
        }

    def _toggle_season(self, season_name):
        """Toggle season expanded/collapsed state"""
        if season_name not in self.season_widgets:
            return

        season_data = self.season_widgets[season_name]
        
        if season_data['expanded']:
            # Collapse
            season_data['episodes_container'].pack_forget()
            season_data['expand_btn'].configure(text="▶")
            season_data['expanded'] = False
        else:
            # Expand
            season_data['episodes_container'].pack(fill="x", padx=(30, 0), after=season_data['header_frame'])
            season_data['expand_btn'].configure(text="▼")
            season_data['expanded'] = True

    def _on_season_checkbox_click(self, season_name):
        """Handle season checkbox click - select/deselect all episodes in season"""
        if self._updating_selection:
            return

        season_data = self.season_widgets.get(season_name)
        if not season_data:
            return

        # Check current state
        all_selected = all(ec['checkbox'].get() for ec in season_data['episode_checkboxes'])
        
        self._updating_selection = True
        try:
            if all_selected:
                # Deselect all
                for ec in season_data['episode_checkboxes']:
                    ec['checkbox'].deselect()
            else:
                # Select all
                for ec in season_data['episode_checkboxes']:
                    ec['checkbox'].select()
            
            self._update_season_counter(season_name)
            self.selection_changed()
        finally:
            self._updating_selection = False

    def _on_episode_checkbox_click(self, episode_index):
        """Handle individual episode checkbox click"""
        if self._updating_selection:
            return

        # Find which season this episode belongs to
        for season_name, season_data in self.season_widgets.items():
            for ec in season_data['episode_checkboxes']:
                if ec['index'] == episode_index:
                    self._update_season_counter(season_name)
                    self.selection_changed()
                    return

    def _update_season_counter(self, season_name):
        """Update season checkbox state and counter based on episode selections"""
        season_data = self.season_widgets.get(season_name)
        if not season_data:
            return

        selected_count = sum(1 for ec in season_data['episode_checkboxes'] if ec['checkbox'].get())
        total = season_data['total_episodes']

        # Update counter text
        if isinstance(season_name, int) or (isinstance(season_name, str) and season_name.isdigit()):
            counter_text = f"{season_name} сезон ({selected_count}/{total})"
        else:
            counter_text = f"{season_name} ({selected_count}/{total})"
        
        season_data['season_label'].configure(text=counter_text)

        # Update season checkbox state
        self._updating_selection = True
        try:
            if selected_count == total:
                season_data['season_checkbox'].select()
            else:
                season_data['season_checkbox'].deselect()
        finally:
            self._updating_selection = False

    def select_all(self):
        """Select all episodes in all seasons"""
        self._updating_selection = True
        try:
            if hasattr(self, 'checkboxes'):  # Flat list mode
                for checkbox in self.checkboxes:
                    checkbox.select()
            else:  # Seasonal mode
                for season_data in self.season_widgets.values():
                    for ec in season_data['episode_checkboxes']:
                        ec['checkbox'].select()
                    self._update_season_counter(season_name) if (season_name := list(self.season_widgets.keys())[list(self.season_widgets.values()).index(season_data)]) else None
        finally:
            self._updating_selection = False

        self.selection_changed()

    def clear_all(self):
        """Clear all selections"""
        self._updating_selection = True
        try:
            if hasattr(self, 'checkboxes'):  # Flat list mode
                for checkbox in self.checkboxes:
                    checkbox.deselect()
            else:  # Seasonal mode
                for season_name, season_data in self.season_widgets.items():
                    for ec in season_data['episode_checkboxes']:
                        ec['checkbox'].deselect()
                    self._update_season_counter(season_name)
        finally:
            self._updating_selection = False

        self.selection_changed()

    def get_selected(self):
        """Return selected episodes in the order of the original episodes list"""
        result = []

        if hasattr(self, 'checkboxes') and self.checkboxes:  # Flat list mode
            for index, checkbox in enumerate(self.checkboxes):
                if checkbox.get():
                    result.append(self.episodes[index])
        else:  # Seasonal mode
            # Maintain original order by iterating through self.episodes
            for index, item in enumerate(self.episodes):
                # Check if this episode is selected
                selected = False
                for season_data in self.season_widgets.values():
                    for ec in season_data['episode_checkboxes']:
                        if ec['index'] == index and ec['checkbox'].get():
                            selected = True
                            break
                    if selected:
                        break
                if selected:
                    result.append(item)

        return result

    def selection_changed(self):
        if self.selection_callback:
            self.selection_callback(self.get_selected())
