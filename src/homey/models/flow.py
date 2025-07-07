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
    lastExecuted: Optional[str] = Field(None, description="Last execution time")
    executionCount: Optional[int] = Field(None, description="Execution count")
    advanced: bool = Field(False, description="Whether this is an advanced flow")

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

    def is_advanced(self) -> bool:
        """Check if this is an advanced flow."""
        return self.advanced

    def get_trigger(self) -> Optional[FlowCard]:
        """Get the trigger card."""
        return self.trigger

    def get_conditions(self) -> List[FlowCard]:
        """Get the condition cards."""
        return self.conditions or []

    def get_actions(self) -> List[FlowCard]:
        """Get the action cards."""
        return self.actions or []

    def get_execution_count(self) -> Optional[int]:
        """Get the execution count."""
        return self.executionCount

    def get_folder_id(self) -> Optional[str]:
        """Get the folder ID."""
        return self.folder

    def __str__(self) -> str:
        """String representation of the flow."""
        status = "enabled" if self.is_enabled() else "disabled"
        if self.is_broken():
            status = "broken"
        return f"Flow(id={self.id}, name={self.name}, status={status})"
