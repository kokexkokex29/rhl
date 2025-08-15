"""
Database utility for managing JSON data storage
Handles clubs, players, and transfer data persistence
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.data_dir = "data"
        self.clubs_file = os.path.join(self.data_dir, "clubs.json")
        self.players_file = os.path.join(self.data_dir, "players.json")
        self.transfers_file = os.path.join(self.data_dir, "transfers.json")
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize JSON files with default structure"""
        default_clubs = {"clubs": {}, "last_updated": None}
        default_players = {"players": {}, "last_updated": None}
        default_transfers = {"transfers": [], "last_updated": None}
        
        if not os.path.exists(self.clubs_file):
            self._write_json(self.clubs_file, default_clubs)
        
        if not os.path.exists(self.players_file):
            self._write_json(self.players_file, default_players)
        
        if not os.path.exists(self.transfers_file):
            self._write_json(self.transfers_file, default_transfers)
    
    def _read_json(self, filename: str) -> Dict:
        """Read JSON file safely"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error reading {filename}: {e}")
            return {}
    
    def _write_json(self, filename: str, data: Dict):
        """Write JSON file safely"""
        try:
            data['last_updated'] = datetime.now().isoformat()
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error writing {filename}: {e}")
    
    # Club management methods
    def get_clubs(self) -> Dict:
        """Get all clubs"""
        return self._read_json(self.clubs_file).get('clubs', {})
    
    def get_club(self, club_id: str) -> Optional[Dict]:
        """Get specific club by ID"""
        clubs = self.get_clubs()
        return clubs.get(club_id)
    
    def add_club(self, club_id: str, name: str, budget: float = 0.0) -> bool:
        """Add new club"""
        try:
            data = self._read_json(self.clubs_file)
            data['clubs'][club_id] = {
                'name': name,
                'budget': budget,
                'players': [],
                'created_at': datetime.now().isoformat()
            }
            self._write_json(self.clubs_file, data)
            return True
        except Exception as e:
            logger.error(f"Error adding club: {e}")
            return False
    
    def update_club_budget(self, club_id: str, new_budget: float) -> bool:
        """Update club budget"""
        try:
            data = self._read_json(self.clubs_file)
            if club_id in data['clubs']:
                data['clubs'][club_id]['budget'] = new_budget
                self._write_json(self.clubs_file, data)
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating club budget: {e}")
            return False
    
    def delete_club(self, club_id: str) -> bool:
        """Delete club"""
        try:
            data = self._read_json(self.clubs_file)
            if club_id in data['clubs']:
                del data['clubs'][club_id]
                self._write_json(self.clubs_file, data)
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting club: {e}")
            return False
    
    # Player management methods
    def get_players(self) -> Dict:
        """Get all players"""
        return self._read_json(self.players_file).get('players', {})
    
    def get_player(self, player_id: str) -> Optional[Dict]:
        """Get specific player by ID"""
        players = self.get_players()
        return players.get(player_id)
    
    def add_player(self, player_id: str, name: str, value: float, club_id: str = None, position: str = '', age: int = 0) -> bool:
        """Add new player"""
        try:
            data = self._read_json(self.players_file)
            data['players'][player_id] = {
                'name': name,
                'value': value,
                'club_id': club_id,
                'position': position,
                'age': age,
                'contract_expires': None,
                'created_at': datetime.now().isoformat()
            }
            self._write_json(self.players_file, data)
            
            # Add player to club if specified
            if club_id:
                self._add_player_to_club(club_id, player_id)
            
            return True
        except Exception as e:
            logger.error(f"Error adding player: {e}")
            return False
    
    def update_player_value(self, player_id: str, new_value: float) -> bool:
        """Update player value"""
        try:
            data = self._read_json(self.players_file)
            if player_id in data['players']:
                data['players'][player_id]['value'] = new_value
                self._write_json(self.players_file, data)
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating player value: {e}")
            return False
    
    def delete_player(self, player_id: str) -> bool:
        """Delete player"""
        try:
            # Remove from players file
            players_data = self._read_json(self.players_file)
            if player_id in players_data['players']:
                club_id = players_data['players'][player_id].get('club_id')
                del players_data['players'][player_id]
                self._write_json(self.players_file, players_data)
                
                # Remove from club if assigned
                if club_id:
                    self._remove_player_from_club(club_id, player_id)
                
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting player: {e}")
            return False
    
    def _add_player_to_club(self, club_id: str, player_id: str):
        """Add player to club's roster"""
        data = self._read_json(self.clubs_file)
        if club_id in data['clubs']:
            if player_id not in data['clubs'][club_id]['players']:
                data['clubs'][club_id]['players'].append(player_id)
                self._write_json(self.clubs_file, data)
    
    def _remove_player_from_club(self, club_id: str, player_id: str):
        """Remove player from club's roster"""
        data = self._read_json(self.clubs_file)
        if club_id in data['clubs']:
            if player_id in data['clubs'][club_id]['players']:
                data['clubs'][club_id]['players'].remove(player_id)
                self._write_json(self.clubs_file, data)
    
    # Transfer management methods
    def get_transfers(self) -> List:
        """Get all transfers"""
        return self._read_json(self.transfers_file).get('transfers', [])
    
    def add_transfer(self, player_id: str, from_club: str, to_club: str, amount: float) -> bool:
        """Record a transfer"""
        try:
            # Update player's club
            players_data = self._read_json(self.players_file)
            if player_id in players_data['players']:
                players_data['players'][player_id]['club_id'] = to_club
                self._write_json(self.players_file, players_data)
            
            # Update club rosters
            if from_club:
                self._remove_player_from_club(from_club, player_id)
            self._add_player_to_club(to_club, player_id)
            
            # Update club budgets
            clubs_data = self._read_json(self.clubs_file)
            if from_club and from_club in clubs_data['clubs']:
                clubs_data['clubs'][from_club]['budget'] += amount
            if to_club in clubs_data['clubs']:
                clubs_data['clubs'][to_club]['budget'] -= amount
            self._write_json(self.clubs_file, clubs_data)
            
            # Record transfer
            transfers_data = self._read_json(self.transfers_file)
            transfers_data['transfers'].append({
                'player_id': player_id,
                'from_club': from_club,
                'to_club': to_club,
                'amount': amount,
                'date': datetime.now().isoformat()
            })
            self._write_json(self.transfers_file, transfers_data)
            
            return True
        except Exception as e:
            logger.error(f"Error recording transfer: {e}")
            return False
