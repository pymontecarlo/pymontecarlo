package pymontecarlo.input.nistmonte;

import gov.nist.microanalysis.NISTMonte.BremsstrahlungEventListener;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.NISTMonte.XRayEventListener2;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

/**
 * Limit the number of showers.
 * 
 * @author ppinard
 */
public class ShowersLimit implements Limit, ActionListener {

    /** Maximum number of trajectories. */
    private final int maxShowers;

    /** Number of simulated trajectories. */
    private long showers;



    /**
     * Creates a new <code>ShowersLimit</code>.
     * 
     * @param showers
     *            maximum number of trajectories
     */
    public ShowersLimit(int showers) {
        if (showers <= 0)
            throw new IllegalArgumentException(
                    "Maximum number of trajectories must be greater than 0");
        this.maxShowers = showers;
    }



    /**
     * Returns the maximum number of showers.
     * 
     * @return maximum number of showers
     */
    public int getMaximumShowers() {
        return maxShowers;
    }



    @Override
    public void setup(MonteCarloSS mcss, XRayEventListener2 xrel,
            BremsstrahlungEventListener bel) {
        mcss.addActionListener(this);
    }



    @Override
    public void actionPerformed(ActionEvent e) {

        switch (e.getID()) {
        case MonteCarloSS.FirstTrajectoryEvent:
            showers = 0;
            break;

        case MonteCarloSS.TrajectoryEndEvent:
            showers += 1;

            if (showers >= maxShowers)
                ((MonteCarloSS) e.getSource()).requestInterruption();

            break;
        default:
            break;
        }
    }
}
