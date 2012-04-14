package pymontecarlo.program.nistmonte.input;

import static org.junit.Assert.assertEquals;

import org.junit.Before;
import org.junit.Test;

public class ShowersLimitTest {

    private ShowersLimit limit;



    @Before
    public void setUp() throws Exception {
        limit = new ShowersLimit(1234);
    }



    @Test
    public void testGetMaximumShowers() {
        assertEquals(1234, limit.getMaximumShowers());
    }

}
