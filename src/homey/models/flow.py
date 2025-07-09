"""Flow model for the Homey API."""

from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import BaseModel


class FlowCard(BaseModel):
    """Represents a flow card."""

    id: Optional[str] = Field(None, description="Card ID")
    uri: Optional[str] = Field(None, description="Card URI")
    title: Optional[str] = Field(None, description="Card title")
    titleFormatted: Optional[str] = Field(None, description="Formatted card title")
    hint: Optional[str] = Field(None, description="Card hint")
    args: Optional[Dict[str, Any]] = Field(None, description="Card arguments")
    tokens: Optional[List[Dict[str, Any]]] = Field(None, description="Card tokens")
    type: Optional[str] = Field(None, description="Card type")
    ownerUri: Optional[str] = Field(None, description="Owner URI")
    droptoken: Optional[str] = Field(None, description="Drop token")

    def __str__(self) -> str:
        """String representation of the flow card."""
        return f"FlowCard(id={self.id}, title={self.title})"


class Flow(BaseModel):
    """Represents a Homey flow."""

    id: Optional[str] = Field(None, description="Flow ID")
    name: Optional[str] = Field(None, description="Flow name")
    type: Optional[str] = Field(None, description="Flow type")
    enabled: bool = Field(True, description="Whether the flow is enabled")
    trigger: Optional[FlowCard] = Field(None, description="Trigger card")
    conditions: Optional[List[FlowCard]] = Field(None, description="Condition cards")
    actions: Optional[List[FlowCard]] = Field(None, description="Action cards")
    folder: Optional[str] = Field(None, description="Folder ID")
    broken: bool = Field(False, description="Whether the flow is broken")

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization processing."""
        # Convert trigger to FlowCard instance
        if self.trigger and isinstance(self.trigger, dict):
            self.trigger = FlowCard(**self.trigger)

        # Convert conditions to FlowCard instances
        if self.conditions:
            conditions = []
            for condition in self.conditions:
                if isinstance(condition, dict):
                    conditions.append(FlowCard(**condition))
                else:
                    conditions.append(condition)
            self.conditions = conditions

        # Convert actions to FlowCard instances
        if self.actions:
            actions = []
            for action in self.actions:
                if isinstance(action, dict):
                    actions.append(FlowCard(**action))
                else:
                    actions.append(action)
            self.actions = actions

    def is_enabled(self) -> bool:
        """Check if the flow is enabled."""
        return self.enabled

    def is_broken(self) -> bool:
        """Check if the flow is broken."""
        return self.broken

    def get_trigger(self) -> Optional[FlowCard]:
        """Get the trigger card."""
        return self.trigger

    def get_conditions(self) -> List[FlowCard]:
        """Get the condition cards."""
        return self.conditions or []

    def get_actions(self) -> List[FlowCard]:
        """Get the action cards."""
        return self.actions or []

    def get_folder_id(self) -> Optional[str]:
        """Get the folder ID."""
        return self.folder

    def __str__(self) -> str:
        """String representation of the flow."""
        status = "enabled" if self.is_enabled() else "disabled"
        if self.is_broken():
            status = "broken"
        return f"Flow(id={self.id}, name={self.name}, status={status})"


class AdvancedFlowBlock(BaseModel):
    """Represents a block in an advanced flow."""

    block_id: str = Field("", description="Block ID")
    id: Optional[str] = Field(None, description="Block owner ID")
    type: Optional[str] = Field(
        None, description="Block type (start, delay, any, all, note)"
    )
    ownerUri: str = Field("", description="card ownerUri")
    x: Optional[int] = Field(None, description="X coordinate on canvas")
    y: Optional[int] = Field(None, description="Y coordinate on canvas")
    args: Optional[Dict[str, Any]] = Field(None, description="Block-specific args")
    outputTrue: Optional[List[str]] = Field(
        None, description="Output true to another block"
    )
    outputFalse: Optional[List[str]] = Field(
        None, description="Output false to another block"
    )
    outputSuccess: Optional[List[str]] = Field(
        None, description="Output success to another block"
    )

    def __str__(self) -> str:
        """String representation of the advanced flow block."""
        return f"AdvancedFlowBlock(id={self.id}, type={self.type})"


class AdvancedFlow(BaseModel):
    """Represents a Homey advanced flow."""

    id: Optional[str] = Field(None, description="Advanced flow ID")
    name: Optional[str] = Field(None, description="Advanced flow name")
    enabled: bool = Field(True, description="Whether the advanced flow is enabled")
    broken: bool = Field(False, description="Whether the advanced flow is broken")
    triggerable: bool = Field(True, description="Whether the flow is triggerable")
    folder: Optional[str] = Field(None, description="Folder ID")
    cards: Dict[str, AdvancedFlowBlock] = Field({}, description="Flow cards")

    # @field_validator("cards", mode="before")
    # @classmethod
    # def convert_cards_to_dict(cls, v: Any) -> Any:
    #     """Convert cards list to dict format if needed."""
    #     if isinstance(v, list):
    #         # Convert list to dict format
    #         cards_dict = {}
    #         for i, card in enumerate(v):
    #             if isinstance(card, dict):
    #                 card_id = card.get("id", f"card-{i}")
    #                 cards_dict[card_id] = card
    #             else:
    #                 # Assume it's already a FlowCard object
    #                 card_id = getattr(card, "id", f"card-{i}") or f"card-{i}"
    #                 cards_dict[card_id] = card
    #         return cards_dict
    #     return v

    def model_dump_compact(self, *args, **kwargs) -> Dict[str, Any]:
        exc = kwargs.get("exclude", [])
        exc.extend(["cards"])
        kwargs["exclude"] = exc
        return self.model_dump(*args, **kwargs)

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization processing."""

        # Convert cards to FlowCard instances
        if self.cards:
            if isinstance(self.cards, dict):
                cards = {}
                for card_id, card_data in self.cards.items():
                    if isinstance(card_data, dict):
                        card_data_copy = card_data.copy()
                        card_data_copy["block_id"] = card_id
                        cards[card_id] = AdvancedFlowBlock(**card_data_copy)
                    elif isinstance(card_data, AdvancedFlowBlock):
                        # Already a FlowCard, just set the ID if not already set
                        if card_data.block_id is None:
                            card_data.block_id = card_id
                        cards[card_id] = card_data
                    else:
                        cards[card_id] = card_data
                self.cards = cards

    def is_enabled(self) -> bool:
        """Check if the advanced flow is enabled."""
        return self.enabled

    def is_broken(self) -> bool:
        """Check if the advanced flow is broken."""
        return self.broken

    def is_triggerable(self) -> bool:
        """Check if the advanced flow is triggerable"""
        return self.triggerable

    def get_cards(self) -> Dict[str, AdvancedFlowBlock]:
        """Get cards as a dictionary with card IDs as keys."""
        return self.cards or {}

    @property
    def cards_count(self) -> int:
        """Get the number of cards in the advanced flow."""
        return len(self.cards) if self.cards else 0

    def get_card_by_id(self, block_id: str) -> Optional[AdvancedFlowBlock]:
        """Get a specific block by ID."""
        return self.cards.get(block_id, None)

    def get_blocks_by_type(self, block_type: str) -> List[AdvancedFlowBlock]:
        """Get all cards of a specific type."""
        if not self.cards:
            return []
        return [block for block in self.cards.values() if block.type == block_type]

    def get_start_cards(self) -> List[AdvancedFlowBlock]:
        """Get all start cards."""
        return self.get_blocks_by_type("start")

    def get_delay_cards(self) -> List[AdvancedFlowBlock]:
        """Get all delay cards."""
        return self.get_blocks_by_type("delay")

    def get_any_cards(self) -> List[AdvancedFlowBlock]:
        """Get all any cards."""
        return self.get_blocks_by_type("any")

    def get_all_cards(self) -> List[AdvancedFlowBlock]:
        """Get all 'all' cards."""
        return self.get_blocks_by_type("all")

    def get_note_cards(self) -> List[AdvancedFlowBlock]:
        """Get all note cards."""
        return self.get_blocks_by_type("note")

    def get_folder_id(self) -> Optional[str]:
        """Get the folder ID."""
        return self.folder

    def has_inline_scripts(self) -> bool:
        """Check if the advanced flow has inline HomeyScript blocks."""
        if not self.cards:
            return False
        return any(card.type == "homey-script" for card in self.cards.values())

    def get_script_cards(self) -> List[AdvancedFlowBlock]:
        """Get all HomeyScript cards."""
        return self.get_blocks_by_type("homey-script")

    def __str__(self) -> str:
        """String representation of the advanced flow."""
        status = "enabled" if self.is_enabled() else "disabled"
        if self.is_broken():
            status = "broken"
        return f"AdvancedFlow(id={self.id}, name={self.name}, status={status})"
